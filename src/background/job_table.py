from database_functions import DatabaseFunctions
from collections import OrderedDict
import json
import uuid
from company_table import CompanyTable
from user_job_table import UserJobTable
from job_location_table import JobLocationTable
from job import Job, Mode
from typing import Dict
from mysql.connector.errors import IntegrityError
from uuid import UUID
from mysql.connector.cursor import MySQLCursor
from mysql.connector.types import RowType, RowItemType
from job_location_table import LocationNotFound


class JobTable: 
    '''
    __get_job_add_query

    gets string query to add a job

    args:
        job_json: dictionary returned from job.to_json() (or sql friendly json)
    returns:
        the query str with %s for injection
    '''
    def __get_add_job_query(job_json : Dict) -> str:
        cols : list[str] = list(job_json.keys())
        col_str : str = ", ".join(cols)
        #Creates a comma separated of %s characters for string replacement when we run the 
        #query
        vals : str = ", ".join(["%s"] * len(cols))
        return f"INSERT INTO Job ({col_str}) VALUES ({vals})"
    '''
    __get_update_str_job

    gets string query to update a job

    args:
        job_json: dictionary returned from job.to_json() (or sql friendly json)
    returns:
        the query str with %s for injection
    '''
    def __get_update_str_job(job_json : Dict) -> str:
        cols : list[str] = list(job_json.keys())
        _ = cols.pop(0)
        col_str : str = "=%s, ".join(cols)
        #add on last replacement str
        col_str = col_str + "=%s"
        update_str : str = f"UPDATE Job SET {col_str} WHERE Job.JobId = %s"
        return update_str
    '''
    __get_most_recent_job_query

    gets string query to read most recent job

    returns:
        literal defined below
    '''
    def __get_most_recent_job_query() -> str:
        return '''SELECT *
        FROM Job
        LEFT JOIN Company
        ON Company.CompanyName = Job.Company
        LEFT JOIN JobLocation
        ON JobLocation.QueryStr = CONCAT(Job.Company, " ", Job.LocationStr)
        ORDER BY TimeAdded DESC'''
    '''
    __get_select_job_by_id_query

    gets string query to read job by id

    returns:
        literal defined below
    '''
    def __get_select_job_by_id_query() -> str:
        return """
        SELECT * 
        FROM JOB
        LEFT JOIN Company
        ON Company.CompanyName = Job.Company
        LEFT JOIN JobLocation
        ON JobLocation.QueryStr = CONCAT(Job.Company, " ", Job.LocationStr)
        WHERE Job.JobID = %s;
        """
    '''
    __get_delete_job_by_id_query

    gets string query to delete job by id

    returns:
        literal defined below
    '''
    def __get_delete_job_by_id_query():
        return f"DELETE FROM Job WHERE JobId=%s"
    '''
    add_job_with_foreign_keys

    adds a job with all foreign keys
        company
        user_job
        job_location
    
    and of course adds the job as well

    args:
        job: job object with foreign keys
        user_id: user UUID for user that "owns" the job
    returns:
        full job with all data for client
    '''
    def add_job_with_foreign_keys(job : Job, user_id_uuid : UUID | str) -> Job:
        user_id : str = str(user_id_uuid)
        #check that the company isn't already in our DB if it isn't then we add it

        # ============== Company ===============
        if not CompanyTable.read_company_by_id(job.company.company_name):
            CompanyTable.add_company(job.company)
            print("COMPANY SUCCESSFULLY ADDED")
        else:
            print("COMPANY ALREADY IN DB")
            job.company = CompanyTable.read_company_by_id(job.company.company_name)
        # =====================================

        # =============== Job =================
        try:
            JobTable.add_job(job)
            print("JOB SUCCESSFULLY ADDED")
        except IntegrityError:
            print("JOB ALREADY IN DB")
        #add the job to the users db
        # =====================================

        # =========== User Job ================
        try:
            UserJobTable.add_user_job(user_id, job.job_id)
            print("USER JOB ADDED")
        except IntegrityError:
            print("USER JOB ALREADY IN DB")
        # =====================================

        # =========== Location ================
        try:
            if job.location_object:
                print("Job sent with location, adding location")
                JobLocationTable.add_job_location(job.location_object, job)
            else:
                try:
                    if job.location_str and job.mode != Mode.REMOTE:
                        print("No location sent, attempting to request from google places")
                        job.location_object = JobLocationTable.get_and_add_location_for_job(job)
                    else:
                        job.location_object = None
                except LocationNotFound:
                    print("COULD NOT FIND LOCATION FOR JOB: " + job.job_name)
                    job.location_object = None
        except IntegrityError:
            print('job location already in DB')
        # ======================================
        return job
    '''
    add_job

    adds a job alone, no foreign keys but placeholders for foreign keys are still added.

    for example, "company" will still point to a company object. if its not there it will error.

    args:
        job: job object with foreign keys
    returns:
        0 if no errors occured
    '''
    def add_job(job: Job) -> int:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        job_json : Dict = job.to_sql_friendly_json()
        job_add_str : str = JobTable.__get_add_job_query(job_json)
        cursor.execute("USE JOBDB")
        try:
            cursor.execute(job_add_str, list(job_json.values()))
        except IntegrityError as e:
            cursor.close()
            raise e
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
    '''
    read_most_recent_job

    reads the most recent job from the db, sorted by timeAdded

    returns:
        Job Object
    '''
    def read_most_recent_job() -> Job | None:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        #Switch to jobDB
        cursor.execute("USE JOBDB")
        query : str = JobTable.__get_most_recent_job_query()
        cursor.execute(query)
        #Grab the first
        result : Dict[str, RowItemType] = cursor.fetchone()
        print("Returning most recent job of " + result)
        if not result:
            return None
        cursor.close()
        return Job.create_with_sql_row(result)
    '''
    read_most_recent_job

    reads job by id arg

    args:
        job_id, string job id from linkedin
    returns:
        Job Object
    '''
    def read_job_by_id(job_id : str) -> Job | None:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        query : str = JobTable.__get_select_job_by_id_query()
        #Switch to JOBDB
        cursor.execute("USE JOBDB")
        #Pass the job Id to be inserted into the query
        cursor.execute(query, (job_id,))
        result : Dict[str, RowItemType] = cursor.fetchone()
        if not result:
            return None
        print("Read job with id " + job_id + " of ")
        print(result)
        cursor.close()
        return Job.create_with_sql_row(result)
    '''
    update_job

    matches job id of the job object to the values of the job object.

    Updates what the foreign keys point to but not the values

    args:
        job, job object to be updated
    returns:
        0 if no errors occured
    '''
    def update_job(job: Job) -> int:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        job_json : Dict = job.to_sql_friendly_json()
        #Grab the specific update columns to add to our query
        update_str : str = JobTable.__get_update_str_job(job_json)
        #convert the values of our json to a list
        #Our list will retain order
        params : list = list(job_json.values())
        _ = params.pop(0)
        #add the job Id to the json
        params.append(job_json["jobId"])
        cursor.execute("USE JOBDB")
        #Execute the query
        cursor.execute(update_str, params)
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        #return success
        return 0
    '''
    delete_job_by_id

    deletes job with the id passed

    args:
        job_id str job id from linkedin
    returns:
        0 if no errors occured
    '''
    def delete_job_by_id(job_id):
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = JobTable.__get_delete_job_by_id_query()
        #Run the sql to delete the job
        cursor.execute(query, (job_id,))
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
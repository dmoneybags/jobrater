from collections import OrderedDict
from database_functions import DatabaseFunctions
from mysql.connector.errors import IntegrityError
import json
from uuid import UUID
from mysql.connector.cursor import MySQLCursor
from job import Job
from typing import Dict
from mysql.connector.types import RowType, RowItemType


class UserJobTable:
    '''
    get_add_user_job_query

    gets the query to add a user_job into the db

    args:
        None
    returns:
        string query
    '''
    def __get_add_user_job_query() -> str:
        return """
            INSERT INTO UserJob (UserJobId, UserId, JobId) VALUES (%s, %s, %s)
        """
    '''
    get_delete_user_job_query

    gets the query to delete a user_job into the db

    args:
        None
    returns:
        string query
    '''
    def __get_delete_user_job_query() -> str:
        return """
            DELETE FROM UserJob WHERE UserJobId = %s
        """
    '''
    get_read_user_jobs_query

    gets the query to read a user_job from the db by user id

    args:
        None
    returns:
        string query
    '''
    def __get_read_user_jobs_query() -> str:
        return f"""
        SELECT Job.*
        FROM Job
        JOIN UserJob ON Job.JobId = UserJob.JobId
        WHERE UserJob.UserId = %s;
        """
    '''
    add_user_job

    adds a user job into the db

    args:
        user_id the UUID user_id
        job_id the id of the job as a str
    returns
        0 if no errors occured
    '''
    def add_user_job(user_id_uuid : UUID | str, job_id : str) -> int:
        user_id : str = str(user_id_uuid)
        print("ADDING USER JOB WITH USER ID " + user_id + " AND JOB ID OF " + job_id)
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = UserJobTable.__get_add_user_job_query()
        #Hashing!!! ahhhh Scary!
        #Just ensures that we have a unique combo of userIds to jobIds, no duplicants
        #Client will check this as well for less eronious calls
        user_job_id : str = str(hash(user_id + job_id))
        try:
            cursor.execute(query, (user_job_id, user_id, job_id))
        except IntegrityError as e:
            cursor.close()
            print("USER JOB ALREADY IN DB")
            raise e
        print("USER JOB SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
    '''
    delete_user_job

    deletes the user job from the db

    args:
        user_id the UUID user id
        job_id the string job id
    returns
        0 if no error occured
    '''
    def delete_user_job(user_id_uuid : UUID | str, job_id : str) -> int:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        user_id : str = str(user_id_uuid)
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = UserJobTable.__get_delete_user_job_query()
        user_job_id : str = str(hash(user_id + job_id))
        cursor.execute(query, (user_job_id,))
        print("USER JOB SUCCESSFULLY DELETED")
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
    '''
    get_user_job

    gets all user jobs from db

    args:
        user_id the UUID user id
    returns
        list of all jobs as job objectw
    '''
    def get_user_jobs(user_id_uuid: UUID | str) -> list[Job]:
        DatabaseFunctions.MYDB.reconnect()
        cursor: MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        user_id : str = str(user_id_uuid)
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = UserJobTable.__get_read_user_jobs_query()
        cursor.execute(query, (user_id,))
        
        results: list[Dict[str, RowItemType]] = cursor.fetchall()
        results_list : list[Job] = [Job.create_with_sql_row(row) for row in results]
        cursor.close()
        return results_list
    
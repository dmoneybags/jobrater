from collections import OrderedDict
from database_functions import DatabaseFunctions
from location_finder import LocationFinder
from job import Job
from typing import Dict
from mysql.connector.cursor import MySQLCursor
from location import Location
from mysql.connector.errors import IntegrityError
from mysql.connector.types import RowType, RowItemType

class LocationNotFound(Exception):
        def __init__(self, data: any, message : str ="LOCATION NOT FOUND "):
            self.message = message + "FOR QUERYSTR: " + str(message)
            super().__init__(self.message)

class JobLocationTable:
    '''
    get_add_location_query

    gets the query to add a JobLocationn

    returns:
        query str
    '''
    def __get_add_location_query(location_json : Dict) -> str:
        cols : list[str] = ["queryStr", "jobId"]
        cols.extend(list(location_json.keys()))
        col_str : str = ", ".join(cols)
        vals : str = ", ".join(["%s"] * len(cols))
        return f"""
        INSERT INTO JobLocation ({col_str}) VALUES ({vals})
        """
    '''
    get_read_location_query

    gets the query to read a JobLocation by the query str

    returns:
        query str
    '''
    def __get_read_location_query() -> str:
        return f"""
        SELECT * FROM JOBLOCATION WHERE QUERYSTR = %s
        """
    '''
    get_and_add_location_for_job

    queries google places api to get location for job and the adds to job_location to db

    args:
        job: doesn't need to have location in fact, should not have location. if a job already has a location use add_job_location
        and split it out of the object
    returns:
        0 if no errors occured
    '''
    def get_and_add_location_for_job(job: Job) -> int:
        #we do sql_friendly here because we dont need all foreign key data
        job_json : Dict = job.to_sql_friendly_json()
        #Queires the google places api
        location : Location | None = LocationFinder.try_get_company_address(job_json["company"], job_json["locationStr"])
        if not location:
            raise(LocationNotFound(job_json))
        return JobLocationTable.add_job_location(location, job)
    '''
    add_job_location

    just adds job location to db, no funny business!

    args:
        location, location object tied to the job
        job, job object of the job
    returns:
        0 if no error occured
    '''
    def add_job_location(location : Location, job : Job) -> int:
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        print("ADDING JOB LOCATION")
        #we do sql_friendly here because we dont need all foreign key data
        job_json : Dict = job.to_sql_friendly_json()
        company : str = job_json["company"]
        location_str : str = job_json["locationStr"]
        query_str : str = company + " " + location_str
        print(f"QUERY_STR: {query_str}")
        location_json : Dict = location.to_json()
        #unpack values
        params = [query_str, job_json["jobId"], *list(location_json.values())]
        query = JobLocationTable.__get_add_location_query(location_json)
        try:
            cursor.execute(query, params)
            DatabaseFunctions.MYDB.commit()
        except IntegrityError:
            cursor.close()
            print("Job location already in db")
        print(f"ADDED JOB")
        cursor.close()
        return 0
    '''
    try_read_location

    reads the company location based on the company and location str given

    args:
        company, str company name
        location_str the string of the location parameter
    returns:
        location object or none if nothing was found
    '''
    def try_read_location(company : str, location_str : str) -> Location | None:
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        print("READING LOCATION OBJECT")
        query_str : str = company + " " + location_str
        print(f"QUERY_STR: {query_str}")
        query : str = JobLocationTable.__get_read_location_query()
        cursor.execute(query, (query_str,))
        result : (Dict[str, RowItemType]) = cursor.fetchone()
        if not result:
            return None
        return Location.try_get_location_from_sql_row(result)
from decimal import Decimal
from enum import Enum, IntEnum
from datetime import datetime
from company import Company
from location import Location
from mysql.connector.types import RowType, RowItemType
from typing import Dict
from location_finder import LocationFinder

class JobInvalidData(Exception):
        def __init__(self, data: any, message : str ="INVALID DATA PASSED TO CONSTRUCTOR"):
            self.message = message + "DATA RECIEVED: " + str(message)
            super().__init__(self.message)

class PaymentFrequency(Enum):
    '''
    PaymentFrequency

    helper class for payment frequencies
    '''
    HOURLY = 1
    YEARLY = 2
class Mode(IntEnum):
    '''
    Mode

    helper class for job in person modes
    '''
    REMOTE = 1
    HYBRID = 2
    ONSITE = 3

class Job:
    '''
    __init__

    creates a job object with the given data
    
    args:
        job_id: the job_id from the linkedIn url
        applicants: the number of applicants scraped from linkedin
        career_stage: the career stage scraped from linkedin
        job_name: the job name scraped from linkedin
        company: a fully formed company object, optional, can create job without company
        payment_base: low end of a salary range ex: 100,000 -> 130,000 payment base is 100,000
        payment_freq: custom paymentFrequency object in the enum defined above
        payment high: ex: 100,000 -> 130,000 payment high is 130,000
        location_str: location string scraped from linkedin
        mode: custom mode object from the enum defined above, represents the jobs WFH policy
        seconds_posted_ago: the number of seconds since the job was posted
        time_added: date_time that we added the job to our db
        location_object: Optional the location object correlating to the jobs location from google places
    returns:
        job object with given data
    '''
    def __init__(self, job_id : str, applicants : int, career_stage : str, job_name : str, company : Company | None, 
                 payment_base : Decimal | None, payment_freq : PaymentFrequency | None, payment_high : Decimal | None, location_str : str,
                 mode: Mode, seconds_posted_ago : int, time_added : datetime, location_object : Location | None) -> None:
        self.job_id : str = job_id
        self.applicants : int = applicants
        self.career_stage : str = career_stage
        self.job_name : str = job_name
        self.company : Company | None = company
        self.payment_base : Decimal | None = payment_base
        self.payment_freq : PaymentFrequency | None = payment_freq
        self.payment_high : Decimal | None = payment_high
        self.location_str : str | None = location_str
        self.mode : Mode = mode
        self.seconds_posted_ago : int = seconds_posted_ago
        self.time_added : datetime = time_added
        self.location_object : Location = location_object
    '''
    str_to_mode

    turns a str mode into a Mode type mode

    args:
        mode_str: the mode string (usually loaded from sql database or json request)
    returns:
        Mode object
    '''
    def str_to_mode(mode_str : str) -> Mode:
        mode_strs : list[str] = ["Remote", "Hybrid", "On-site"]
        enum_value : int = mode_strs.index(mode_str) + 1
        return Mode(enum_value)
    '''
    mode_to_str

    turns a mode object into a str for serialization

    args:
        mode: Mode, the mode object
    returns:
        mode str
    '''
    def mode_to_str(mode: Mode) -> str:
        mode_strs : list[str] = ["Remote", "Hybrid", "On-site"]
        return mode_strs[mode.value - 1]
    '''
    create_with_sql_row

    creates a job object from a sql row returned from the cursor

    args:
        sql_query_row result of a cursor executing a select
    returns:
        Job object
    '''
    @classmethod
    def create_with_sql_row(cls, sql_query_row: (Dict[str, RowItemType])) -> 'Job':
        company : Company | None = Company.try_create_with_sql_row(sql_query_row)
        location : Location | None = Location.try_get_location_from_sql_row(sql_query_row)
        job_id : str = sql_query_row["JobId"]
        applicants : int = int(sql_query_row["Applicants"])
        career_stage : str = sql_query_row["CareerStage"]
        job_name : str = sql_query_row["Job"]
        payment_base : Decimal = sql_query_row["PaymentBase"]
        try:
            payment_freq : PaymentFrequency = sql_query_row["PaymentFreq"]
        except KeyError:
            payment_freq = None
        try:
            payment_high : Decimal = sql_query_row["PaymentHigh"]
        except KeyError:
            payment_high = None
        try:
            location_str : str = sql_query_row["LocationStr"]
        except KeyError:
            location_str = None
        mode : Mode = Job.str_to_mode(sql_query_row["Mode"])
        seconds_posted_ago : int = sql_query_row["SecondsPostedAgo"]
        time_added : datetime = sql_query_row["TimeAdded"]
        return cls(job_id, applicants, career_stage, job_name, company, payment_base, payment_freq, payment_high, location_str, mode, seconds_posted_ago,
                   time_added, location)
    '''
    create_with_json

    creates a job object from json returned from request

    args:
        json from request
    returns:
        Job object
    '''
    @classmethod
    def create_with_json(cls, json_object : Dict) -> 'Job':
        company : Company | None = Company.try_create_with_json(json_object["company"])
        try:
            json_object["location"]["addressStr"]
        except KeyError:
            location : Location | None = LocationFinder.try_get_company_address(json_object["company"], json_object["locationStr"])
        job_id : str = json_object["jobId"]
        applicants : int = int(json_object["applicants"])
        career_stage : str = json_object["careerStage"]
        job_name : str = json_object["job"]
        try:
            payment_base : Decimal = json_object["paymentBase"]
        except KeyError:
            payment_base = None
        try:
            payment_freq : PaymentFrequency = json_object["paymentFreq"]
        except KeyError:
            payment_freq = None
        try:
            payment_high : Decimal = json_object["paymentHigh"]
        except KeyError:
            payment_high = None
        try:
            location_str : str = json_object["locationStr"]
        except KeyError:
            location_str = None
        mode : Mode = Job.str_to_mode(json_object["mode"])
        seconds_posted_ago : int = json_object["secondsPostedAgo"]
        try:
            time_added : datetime = datetime.fromtimestamp(float(json_object["timeAdded"]))
        except KeyError:
            time_added = None
        return cls(job_id, applicants, career_stage, job_name, company, payment_base, payment_freq, payment_high, location_str, mode, seconds_posted_ago,
                   time_added, location)
    '''
    to_json

    dumps job to json, includes all fks

    args:
        None
    returns:
        Dict
    '''
    def to_json(self) -> Dict:
        return {
            "jobId" : self.job_id,
            "applicants" : self.applicants,
            "careerStage" : self.career_stage,
            "jobName" : self.job_name,
            "company" : self.company.to_json(),
            "paymentBase" : str(self.payment_base),
            "paymentFreq" : self.payment_freq,
            "locationStr" : self.location_str,
            "mode" : Job.mode_to_str(self.mode),
            "secondsPostedAgo" : self.seconds_posted_ago,
            "timeAdded" : str(int(self.timeAdded.timestamp())),
            "locationObject" : self.location_object.to_json()
        }
    '''
    to_sql_friendly_json

    dumps job to json friendly for our sql queries where the company object is stored as 
    fk.

    args:
        None
    returns:
        Dict
    '''
    def to_sql_friendly_json(self) -> Dict:
        sql_friendly_dict : Dict = {
            "jobId" : self.job_id,
            "applicants" : self.applicants,
            "careerStage" : self.career_stage,
            "job" : self.job_name,
            "company" : self.company.company_name,
            "paymentBase" : str(self.payment_base),
            "paymentFreq" : self.payment_freq,
            "locationStr" : self.location_str,
            "mode" : Job.mode_to_str(self.mode),
            "secondsPostedAgo" : self.seconds_posted_ago
        }
        if self.time_added:
            sql_friendly_dict["timeAdded"] = str(int(self.timeAdded.timestamp()))
        if self.location_object:
            sql_friendly_dict["location"] = self.location_object.to_json()
        return sql_friendly_dict

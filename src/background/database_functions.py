'''
TO DO: 
*CRUD methods for company CHECK
*change our query for adding the job to be created programatically with a
    "Get job values" function and then a "generate job query" function
    All our querys should be generated this way CHECK
*Change the glassdoor calls to check if the company is already in our db CHECK

'''

'''
Execution flow:

Background.js

Listens for: a tab change event fired when the current tabs url changes
Executes: scrapes the jobId from the url
Sends: a message to the contentScript that we recieved a new job
\/
\/
ContentScript.js
Listens for: the new job event from background.js
Executes the scraping of the linkedin and glassdoor
Calls:
\/
\/
database_server.py
Listens for: requests sent on PORT 5001
Executes the database functions to CRUD jobs
Through routines in
\/
\/
database_functions.py

TO DO:

make sure that when we check if the company exists all the values arent null
'''
#TO DO, we should not just leave cursor open

import mysql.connector
import json
import os
import uuid
from decimal import Decimal
import datetime
from collections import OrderedDict
from google_places import get_company_location_object
from company_controller import CompanyTable
from job_controller import JobController
from keyword_controller import KeywordController
from location_controller import LocationController
from user_controller import UserController
from user_job_controller import UserJobController

#Columns in our DB
JOB_COLUMNS = ["jobId", "applicants", "careerStage", 
        "company", "job", "KeywordID", "location", "mode", 
        "paymentBase", "paymentFreq", "paymentHigh", "secondsPostedAgo"]
#The columns in our keyword db
KEYWORD_COLUMNS = ["KeywordID", "Keyword1", "Keyword2", "Keyword3", "Keyword4", "Keyword5", "Keyword6",
        "Keyword7", "Keyword8", "Keyword9", "Keyword10"]
#The columns in our company db
COMPANY_COLUMNS = ["company", "businessOutlookRating", "careerOpportunitiesRating", "ceoRating",
                "compensationAndBenefitsRating", "cultureAndValuesRating", "diversityAndInclusionRating",
                "overallRating", "seniorManagementRating", "workLifeBalanceRating"]
#The columns in our user db
#very basic colums for testing, moving forward we will have more advanced data
USER_COLUMNS = ["userId", "email", "password", "google_Id", "name", "location","salt"]
#a custom json decoder, needed because our items in our DB are stored as Decimals
#and datetimes
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return str(obj)
        #if its not either just return the object
        return super().default(obj)
 

class DatabaseFunctions:
    #Right now we'll connect to our localhost
    HOST = "localhost"
    MYSQLUSER = "root"
    #Grab our sql password from our .zshenv file
    MYSQLPASSWORD = os.getenv("SQLPASSWORD")
    MYDB = mysql.connector.connect(
        host=HOST,
        user=MYSQLUSER,
        password=MYSQLPASSWORD
    )
    #Create the database (I just ran it in shell)
    def run_sql_file(f):
        cursor = DatabaseFunctions.MYDB.cursor()
        with open(f, "r") as sqlFile:
            cursor.execute(sqlFile.read(), multi=True)
        DatabaseFunctions.MYDB.commit()
    #returns a list of string column names when given a str table name
    def get_columns_from_table(table):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        query = f"SELECT * FROM {table} LIMIT 1;"
        cursor.execute(query)
        #consume our unused query
        _ = cursor.fetchall()
        columns = cursor.column_names
        #func to turn strings lowercase
        first_letter_lower = lambda s: s[:1].lower() + s[1:] if s else ''
        columns = [first_letter_lower(c) for c in columns]
        return columns
    #Create company
    #Yes it takes an arg of job_json but theoretically could be called on simply company_json
    def add_company(job_json):
        return CompanyTable.add_company(job_json)
    #Read company
    def read_company_by_id(company_name):
        return CompanyTable.read_company_by_id(company_name)
    #Update company
    def update_company(job_json):
        return CompanyTable.update_company(job_json)
    #Delete company
    def delete_company(company):
        return CompanyTable.delete_company_by_name(company)
    #Create keywords
    def add_keywords(job_json, keyword_uuid_str):
        return KeywordController.add_keywords(job_json, keyword_uuid_str)
    #Create job
    def add_job(job_json, user_id):
        return JobController.add_job
    #Read most recent job
    #Mostly for test code, in reality index.html will work by grabbing an event of the most recent id
    def read_most_recent_job():
        return JobController.read_most_recent_job()
    #Grabs job by id
    def read_job_by_id(job_id):
        return JobController.read_job_by_id(job_id)
    #Update Job
    #TO DO: Add support for updating keywords
    def update_job(job_json):
        return JobController.update_job(job_json)
    #Delete Job
    #takes an argument of the string job id
    def delete_job(job_id):
        return JobController.delete_job(job_id)
    #Read User using the email as primary key
    #Takes an arg of the string email
    #Returns a string for responses should probably be changed tbh
    def read_user_by_email(email):
        return UserController.read_user_by_email(email)
    #Read User using the email as primary key
    #Takes an arg of the string email
    def read_user_by_googleId(googleId):
        return UserController.read_user_by_googleId(googleId)
    #Adds a user upon the server recieving the json
    def add_user(user_json, salt):
        return UserController.add_user(user_json, salt)
    def delete_user(email):
        return UserController.delete_user(email)
    def add_user_job(user_id, job_id):
        return UserJobController(user_id, job_id)
    def delete_user_job(user_id, job_id):
        return UserJobController.delete_user_job(user_id, job_id)
    def get_user_jobs(user_id):
        return UserJobController.get_user_jobs(user_id)
    def get_and_add_location(jobJson):
        return LocationController.get_and_add_location(jobJson)
    def read_location(company, location_str):
        return LocationController.read_location(company, location_str)
    
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
'''

import mysql.connector
import json
import os
import uuid
from decimal import Decimal
import datetime
from collections import OrderedDict

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
USER_COLUMNS = ["userID", "email", "password", "google_Id", "name"]
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
    #Takes in the job json and returns the list of strings that the sql command
    #expect
    def get_job_dict(job_json, keyword_ID):
        #Generate a list of 0s as placeholders
        zero_filled_job_data = {}
        for col in JOB_COLUMNS:
            #Our job data doesn't come with a KeywordID, we generate it on the backend
            if col == "KeywordID":
                zero_filled_job_data[col] = keyword_ID
            if col == "location":
                    zero_filled_job_data["locationStr"] = str(job_json["location"])
                    continue
            try:
                #Does our job has an entry for the value? it always should but just a try-except for safety
                val = str(job_json[col])
                zero_filled_job_data[col] = 0 if val == '' else val
            except KeyError:
                continue
        return zero_filled_job_data
    #Our keyword values are stored in a many to one format
    #Stored as primary key of the keyword being keyword ID
    #and the job db having a corresponing keyword ID Foreign key
    #Returns a json dictionary of the column name to the keyword value
    def get_keyword_values(job_json, keyword_ID):
        #We only want the top 10 keyword
        keywords = job_json["keywords"][:10]
        return [keyword_ID, *keywords]
    #Our company values are added into a separate db, we run this function
    #to get the json dictionary to represent the values for the add
    def get_company_dict(job_json):
        zero_filled_company_data = {}
        for col in COMPANY_COLUMNS:
            try:
                val = str(job_json[col])
                zero_filled_company_data[col] = 0 if val == '' else val
            except KeyError:
                continue
        print("Recieved company dictionary of: " +
            json.dumps(zero_filled_company_data)
        )
        return zero_filled_company_data
    #Generates the sql string to add a company, using string replacement
    def get_company_add_query(company_values):
        cols = list(company_values.keys())
        col_str = ", ".join(cols)
        #Creates a comma separated of %s characters for string replacement when we run the 
        #query
        vals = ", ".join(["%s"] * len(cols))
        return f"INSERT INTO Company ({col_str}) VALUES ({vals})"
    #Generates the query to add a job from the values of our job, as sent by a dictionary
    #This dictionary is generated by get job values
    def get_job_add_query(job_json):
        cols = list(job_json.keys())
        col_str = ", ".join(cols)
        #Creates a comma separated of %s characters for string replacement when we run the 
        #query
        vals = ", ".join(["%s"] * len(cols))
        return f"INSERT INTO Job ({col_str}) VALUES ({vals})"
    def get_keyword_add_query():
        return "INSERT INTO KeywordList (KeywordID, Keyword1, Keyword2, Keyword3, Keyword4, Keyword5, Keyword6, Keyword7, Keyword8, Keyword9, Keyword10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #Function which is called when our update db function is called
    #turns the json into a query for sql
    def get_update_str_job(job_json):
        #We're just updating the job here, no foreign keys
        job_json_without_company_and_keywords = DatabaseFunctions.get_job_dict()
        editted_cols = []
        for key, value in job_json_without_company_and_keywords.items():
            update_key = key
            #Location is a keyword in sql so the column is called locationStr
            if key == "location":
                update_key = "locationStr"
            #%s allows us to inject our values into the string
            editted_cols.append(f"{update_key} = %s")
        col_str = ", ".join(editted_cols)
        update_str = f"UPDATE Job SET {col_str} WHERE JobId = %s"
        return update_str
    #Gets the sql code to update a company
    def get_update_str_company(company_values):
        editted_cols = []
        for key, value in company_values.items():
            #%s allows us to inject our values into the string
            editted_cols.append(f"{key} = %s")
        col_str = ", ".join(editted_cols)
        update_str = f"UPDATE Company SET {col_str} WHERE Company = %s"
        return update_str
    #Returns the query to read the most recent job
    def get_most_recent_job_query():
        return '''SELECT *
        FROM Job
        LEFT JOIN KeywordList
        ON Job.KeywordId = KeywordList.KeywordId
        LEFT JOIN Company
        ON Company.Company = Job.Company
        ORDER BY TimeAdded DESC'''
    def get_select_job_by_id_query():
        return """
            SELECT * 
            FROM JOB
            LEFT JOIN KeywordList
            ON Job.KeywordId = KeywordList.KeywordId
            LEFT JOIN Company
            ON Company.Company = Job.Company
            WHERE JobID = %s;
        """
    def get_delete_job_by_id_query():
        return f"DELETE FROM Job WHERE JobId=%s"
    def get_delete_company_by_name_query():
        return f"DELETE FROM Company WHERE Company=%s"
    def get_select_company_by_name_query():
        return """
            SELECT *
            FROM Company
            WHERE Company = %s;
        """
    def get_read_user_by_email_query():
        return """
            SELECT *
            FROM USER
            WHERE Email = %s;
        """
    def get_read_user_by_googleId_query():
        return """
            SELECT *
            FROM USER
            WHERE Google_Id = %s;
        """
    def get_add_user_query(user_json):
        cols = list(user_json.keys())
        col_str = ", ".join(cols)
        vals = ", ".join(["%s"] * len(cols))
        return f"INSERT INTO User ({col_str}) VALUES ({vals})"
    #Create company
    #Yes it takes an arg of job_json but theoretically could be called on simply company_json
    def add_company(job_json):
        company_values = DatabaseFunctions.get_company_dict(job_json)
        company_add_Str = DatabaseFunctions.get_company_add_query(company_values)
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        cursor.execute(company_add_Str, list(company_values.values()))
        print("COMPANY SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        return 'success', 200
    #Read company
    def read_company_by_id(company_name):
        query = DatabaseFunctions.get_select_company_by_name_query()
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        cursor.execute(query, (company_name,))
        result = cursor.fetchone()
        print(result)
        if not result:
            return None
        # Map column names to values
        result_dict = OrderedDict(zip(COMPANY_COLUMNS, result))
        return json.dumps(result_dict, cls=DecimalEncoder)
    #Update company
    def update_company(job_json):
        company_values = DatabaseFunctions.get_company_dict(job_json)
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        print("RECIEVED MESSAGE TO UPDATE Company WITH ID " + company_values["company"])
        #Grab the specific update columns to add to our query
        update = DatabaseFunctions.get_update_str_company(company_values)
        #convert the values of our json to a list
        #Our list will retain order
        params = list(company_values.values())
        #add the job Id to the json
        params.append(company_values["company"])
        cursor.execute("USE JOBDB")
        #Execute the query
        cursor.execute(update, params)
        DatabaseFunctions.MYDB.commit()
        #return success
        return 'success', 200
    #Delete company
    def delete_company(company):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query = DatabaseFunctions.get_delete_company_by_name_query()
        #Run the sql to delete the job
        cursor.execute(query, (company,))
        DatabaseFunctions.MYDB.commit()
        return 'success', 200
    #Create keywords
    def add_keywords(job_json, keyword_uuid_str):
        keyword_add_str = DatabaseFunctions.get_keyword_add_query()
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        #Grab our json for the keywords
        keywordValues = DatabaseFunctions.get_keyword_values(job_json, keyword_uuid_str)
        cursor.execute(keyword_add_str, keywordValues)
        print("KEYWORDS SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
    #Create job
    def add_job(job_json):
        job_id = job_json["jobId"]
        #The job is already in our db
        #Prevents duplicate keywords
        if (DatabaseFunctions.read_job_by_id(job_id)):
            return 'success', 200
        #Generate a uuid for our keyword db
        keyword_uuid_str = str(uuid.uuid1())
        job_values = DatabaseFunctions.get_job_dict(job_json, keyword_uuid_str)
        job_add_str = DatabaseFunctions.get_job_add_query(job_values)
        DatabaseFunctions.add_keywords(job_json, keyword_uuid_str)
        #check that the company isn't already in our DB if it isn't then we add it
        if not DatabaseFunctions.read_company_by_id(job_values["company"]):
            DatabaseFunctions.add_company(job_json)
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        #grab the job json
        print(job_add_str)
        cursor.execute(job_add_str, list(job_values.values()))
        print("JOB SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        return 'success', 200
    #Read most recent job
    #Mostly for test code, in reality index.html will work by grabbing an event of the most recent id
    def read_most_recent_job():
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to jobDB
        cursor.execute("USE JOBDB")
        #Order the jobs from newest to oldest
        #Grab our keywords as well
        #Select all the jobs but only grab one
        query = DatabaseFunctions.get_most_recent_job_query()
        cursor.execute(query)
        #Grab the first
        result = cursor.fetchone()
        print(result)
        if not result:
            return None
        # Map column names to values
        result_dict = OrderedDict(zip(JOB_COLUMNS, result))
        return json.dumps(result_dict, cls=DecimalEncoder)
    #Grabs job by id
    def read_job_by_id(jobId):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        query = DatabaseFunctions.get_select_job_by_id_query()
        #Switch to JOBDB
        cursor.execute("USE JOBDB")
        #Pass the job Id to be inserted into the query
        cursor.execute(query, (jobId,))
        result = cursor.fetchone()
        print(result)
        if not result:
            return None
        # Map column names to values
        result_dict = OrderedDict(zip(JOB_COLUMNS, result))
        return json.dumps(result_dict, cls=DecimalEncoder)
    #Update Job
    #TO DO: Add support for updating keywords
    def update_job(job_json):
        job_values = DatabaseFunctions.get_company_dict()
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Grab the specific update columns to add to our query
        update = DatabaseFunctions.get_update_str_job(job_values)
        #convert the values of our json to a list
        #Our list will retain order
        params = list(job_values.values())
        #add the job Id to the json
        params.append(job_values["jobId"])
        cursor.execute("USE JOBDB")
        #Execute the query
        cursor.execute(update, params)
        DatabaseFunctions.MYDB.commit()
        #return success
        return 'success', 200
    #Delete Job
    #takes an argument of the string job id
    def delete_job(jobId):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query = DatabaseFunctions.get_delete_job_by_id_query()
        #Run the sql to delete the job
        cursor.execute(query, (jobId,))
        DatabaseFunctions.MYDB.commit()
        return 'success', 200
    #Read User using the email as primary key
    #Takes an arg of the string email
    def read_user_by_email(email):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query = DatabaseFunctions.get_read_user_by_email_query()
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if not result:
            return None
        result_dict = OrderedDict(zip(USER_COLUMNS, result))
        return json.dumps(result_dict, cls=DecimalEncoder)
    #Read User using the email as primary key
    #Takes an arg of the string email
    def read_user_by_googleId(googleId):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query = DatabaseFunctions.get_read_user_by_googleId_query()
        cursor.execute(query, (googleId,))
        result = cursor.fetchone()
        if not result:
            return None
        result_dict = OrderedDict(zip(USER_COLUMNS, result))
        return json.dumps(result_dict, cls=DecimalEncoder)
    #Adds a user upon the server recieving the json
    def add_user(user_json):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query = DatabaseFunctions.get_job_add_query(user_json)
        cursor.execute(query, (user_json.values()))
        print("USER SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        return 'success', 200
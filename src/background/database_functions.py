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
    #Takes in the job json and returns the list of strings that the sql command
    #expect
    def get_job_values(jobJson, keywordID):
        #Columns in our DB
        vals = ["jobId", "applicants", "businessOutlookRating", "careerOpportunitiesRating", "careerStage", 
                "ceoRating", "company", "compensationAndBenefitsRating", "cultureAndValuesRating", 
                "diversityAndInclusionRating", "job", "KeywordID", "location", "mode", "overallRating", 
                "paymentBase", "paymentFreq", "paymentHigh", "secondsPostedAgo", "seniorManagementRating", 
                "workLifeBalanceRating"]
        #Generate a list of 0s as placeholders
        strJobData = [0] * len(vals)
        for i in range(len(vals)):
            #Our job data doesn't come with a KeywordID, we generate it on the backend
            if vals[i] == "KeywordID":
                strJobData[i] = keywordID
            try:
                #Does our job has an entry for the value? it always should but just a try-except for safety
                val = str(jobJson[vals[i]])
                strJobData[i] = 0 if val == '' else val
            except KeyError:
                continue
        return strJobData
    #Our keyword values are stored in a many to one format
    #Stored as primary key of the keyword being keyword ID
    #and the job db having a corresponing keyword ID Foreign key
    #Returns a json dictionary of the column name to the keyword value
    def get_keyword_values(jobJson, keywordID):
        #The columns in our keyword db
        vals = ["KeywordID", "Keyword1", "Keyword2", "Keyword3", "Keyword4", "Keyword5", "Keyword6",
                "Keyword7", "Keyword8", "Keyword9", "Keyword10"]
        #We only want the top 10 keyword
        keywords = jobJson["keywords"][:10]
        return [keywordID, *keywords]
    #Function which is called when our update db function is called
    #turns the json into a query for sql
    def get_update_str(jobJson):
        editted_cols = []
        for key, value in jobJson.items():
            updateKey = key
            #Location is a keyword in sql so the column is called locationStr
            if key == "location":
                updateKey = "locationStr"
            #%s allows us to inject our values into the string
            editted_cols.append(f"{updateKey} = %s")
        return ", ".join(editted_cols)
    #Create job
    def add_job(jobJson):
        #Generate a uuid for our keyword db
        keywordUuidStr = str(uuid.uuid1())
        jobAddStr = "INSERT INTO Job (JobId, Applicants, BusinessOutlookRating, CareerOpportunitiesRating, CareerStage, CeoRating, Company, CompensationAndBenefitsRating, CultureAndValuesRating, DiversityAndInclusionRating, Job, KeywordID, LocationStr, Mode, OverallRating, PaymentBase, PaymentFreq, PaymentHigh, SecondsPostedAgo, SeniorManagementRating, WorkLifeBalanceRating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        keywordAddStr = "INSERT INTO KeywordList (KeywordID, Keyword1, Keyword2, Keyword3, Keyword4, Keyword5, Keyword6, Keyword7, Keyword8, Keyword9, Keyword10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        #Grab our json for the keywords
        keywordValues = DatabaseFunctions.get_keyword_values(jobJson, keywordUuidStr)
        cursor.execute(keywordAddStr, keywordValues)
        print("KEYWORDS SUCCESSFULLY ADDED")
        #grab the job json
        jobValues = DatabaseFunctions.get_job_values(jobJson, keywordUuidStr)
        cursor.execute(jobAddStr, jobValues)
        print("JOB SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        return '', 204
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
        cursor.execute(
        '''SELECT *
        FROM JOB
        LEFT JOIN KeywordList
        ON JOB.KeywordId = KeywordList.KeywordId
        ORDER BY TimeAdded DESC''')
        #Grab the first
        query = cursor.fetchone()
        print(query)
        #Convert the response to json
        return json.dumps(query, cls=DecimalEncoder)
    #Grabs job by id
    def read_job_by_id(jobId):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        query = """
            SELECT *
            FROM JOB
            LEFT JOIN KeywordList ON JOB.KeywordId = KeywordList.KeywordId
            WHERE JobID = %s;
        """
        #Switch to JOBDB
        cursor.execute("USE JOBDB")
        #Pass the job Id to be inserted into the query
        cursor.execute(query, (jobId,))
        query = cursor.fetchone()
        print(query)
        #Conver the response to json
        return json.dumps(query, cls=DecimalEncoder)
    #Update Job
    #TO DO: Add support for updating keywords
    def update_job(jobJson):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        print("RECIEVED MESSAGE TO UPDATE JOB WITH ID " + jobJson["jobId"])
        #Grab the specific update columns to add to our query
        update_str = DatabaseFunctions.get_update_str(jobJson)
        query = f"UPDATE Job SET {update_str} WHERE JobId = %s"
        #convert the values of our json to a list
        #Our list will retain order
        params = list(jobJson.values())
        #add the job Id to the json
        params.append(jobJson["jobId"])
        cursor.execute("USE JOBDB")
        #Execute the query
        cursor.execute(query, params)
        DatabaseFunctions.MYDB.commit()
        #return success
        return '', 204
    #Delete Job
    #takes an argument of the string job id
    def delete_job(jobId):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        #Run the sql to delete the job
        cursor.execute(f"DELETE FROM Job WHERE JobId={jobId}")
        DatabaseFunctions.MYDB.commit()
        return '', 204

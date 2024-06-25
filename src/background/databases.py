import mysql.connector
import json
import os
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
from decimal import Decimal
import datetime

app = Flask(__name__)
CORS(app)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return str(obj)
        return super().default(obj)
 

class DatabaseFunctions:
    HOST = "localhost"
    MYSQLUSER = "root"
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
    def get_keyword_values(jobJson, keywordID):
        vals = ["KeywordID", "Keyword1", "Keyword2", "Keyword3", "Keyword4", "Keyword5", "Keyword6",
                "Keyword7", "Keyword8", "Keyword9", "Keyword10"]
        keywords = jobJson["keywords"][:10]
        return [keywordID, *keywords]
    def get_update_str(jobJson):
        editted_cols = []
        for key, value in jobJson.items():
            updateKey = key
            if key == "location":
                updateKey = "locationStr"
            editted_cols.append(f"{updateKey} = %s")
        return ", ".join(editted_cols)
    #Create job
    def add_job(jobJson):
        keywordUuidStr = str(uuid.uuid1())
        jobAddStr = "INSERT INTO Job (JobId, Applicants, BusinessOutlookRating, CareerOpportunitiesRating, CareerStage, CeoRating, Company, CompensationAndBenefitsRating, CultureAndValuesRating, DiversityAndInclusionRating, Job, KeywordID, LocationStr, Mode, OverallRating, PaymentBase, PaymentFreq, PaymentHigh, SecondsPostedAgo, SeniorManagementRating, WorkLifeBalanceRating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        keywordAddStr = "INSERT INTO KeywordList (KeywordID, Keyword1, Keyword2, Keyword3, Keyword4, Keyword5, Keyword6, Keyword7, Keyword8, Keyword9, Keyword10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        keywordValues = DatabaseFunctions.get_keyword_values(jobJson, keywordUuidStr)
        cursor.execute(keywordAddStr, keywordValues)
        print("KEYWORDS SUCCESSFULLY ADDED")
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
        cursor.execute("USE JOBDB")
        cursor.execute(
        '''SELECT *
        FROM JOB
        LEFT JOIN KeywordList
        ON JOB.KeywordId = KeywordList.KeywordId
        ORDER BY TimeAdded DESC''')
        query = cursor.fetchone()
        print(query)
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
        cursor.execute("USE JOBDB")
        cursor.execute(query, (jobId,))
        query = cursor.fetchone()
        print(query)
        return json.dumps(query, cls=DecimalEncoder)
    #Update Job
    #TO DO: Add support for updating keywords
    def update_job(jobJson):
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        print("RECIEVED MESSAGE TO UPDATE JOB WITH ID " + jobJson["jobId"])
        update_str = DatabaseFunctions.get_update_str(jobJson)
        query = f"UPDATE Job SET {update_str} WHERE JobId = %s"
        params = list(jobJson.values())
        params.append(jobJson["jobId"])
        cursor.execute("USE JOBDB")
        cursor.execute(query, params)
        DatabaseFunctions.MYDB.commit()
        return '', 204
    #Delete Job
    @app.route('/databases/delete_job', methods=['POST'])
    def delete_job():
        cursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        cursor.execute("USE JOBDB")
        cursor.execute(f"DELETE FROM Job WHERE JobId={jobId}")
        DatabaseFunctions.MYDB.commit()
        return '', 204
class DatabaseServer:
    @app.route('/databases/add_job', methods=['POST'])
    def add_job():
        jobJson = json.loads(request.args.get('jobJson', default="NO JOB JSON LOADED", type=str))
        print("RECIEVED MESSAGE TO ADD JOB WITH ID " + jobJson["jobId"])
        return DatabaseFunctions.add_job(jobJson)
    @app.route('/databases/read_most_recent_job', methods=['GET'])
    def read_most_recent_job():
        return DatabaseFunctions.read_most_recent_job()
    @app.route('/databases/read_job_by_id', methods=['GET'])
    def read_job_by_id():
        jobId = json.loads(request.args.get('jobId', default="NO JOB ID LOADED", type=str))
        return DatabaseFunctions.read_job_by_id(jobId)
    @app.route('/databases/update_job', methods=['POST'])
    def update_job():
        jobJson = json.loads(request.args.get('jobJson', default="NO JOB JSON LOADED", type=str))
        return DatabaseFunctions.update_job(jobJson)
    @app.route('/databases/delete_job', methods=['POST'])
    def delete_job():
        jobId = json.loads(request.args.get('jobId', default="NO JOB ID LOADED", type=str))
        return DatabaseFunctions.delete_job(jobId)
if __name__ == '__main__':
    app.run(debug=True, port=5001)
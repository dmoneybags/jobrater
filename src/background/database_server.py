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
'''

from flask import Flask
from database_functions import DatabaseFunctions
from flask import Flask, jsonify, request
from flask_cors import CORS
import json

#Set up our server using flask
app = Flask(__name__)
#Give support for cross origin requests from our content Script
CORS(app)

class DatabaseServer:
    @app.route('/databases/add_job', methods=['POST'])
    def add_job():
        #Load the job data from the request, it is the the form of a string
        #so we load it into json using json.loads
        jobJson = json.loads(request.args.get('jobJson', default="NO JOB JSON LOADED", type=str))
        print("RECIEVED MESSAGE TO ADD JOB WITH ID " + jobJson["jobId"])
        #Call the database function to execute the insert
        return DatabaseFunctions.add_job(jobJson)
    @app.route('/databases/read_most_recent_job', methods=['GET'])
    def read_most_recent_job():
        #Call the database function to select and sort to the most recent job
        return DatabaseFunctions.read_most_recent_job()
    @app.route('/databases/read_job_by_id', methods=['GET'])
    def read_job_by_id():
        #Grab the jobId from the request, it is in the form of a string
        jobId = json.loads(request.args.get('jobId', default="NO JOB ID LOADED", type=str))
        return DatabaseFunctions.read_job_by_id(jobId)
    @app.route('/databases/update_job', methods=['POST'])
    def update_job():
        #We take an argument of the whole job data in the from a json string
        jobJson = json.loads(request.args.get('jobJson', default="NO JOB JSON LOADED", type=str))
        return DatabaseFunctions.update_job(jobJson)
    @app.route('/databases/delete_job', methods=['POST'])
    def delete_job():
        #Get the job id from the request
        jobId = json.loads(request.args.get('jobId', default="NO JOB ID LOADED", type=str))
        #run the sql code
        return DatabaseFunctions.delete_job(jobId)
    #We only give the server an option to read companies,
    #theres no reason for us to make calls to update or delete companies yet
    @app.route('/databases/read_company', methods=["GET"])
    def read_job():
        company = json.loads(request.args.get('company', default="NO COMPANY LOADED", type=str))
        result = DatabaseFunctions.read_company_by_id(company)
        if not result:
            return 'Company not found', 404
        return result
if __name__ == '__main__':
    #Run the app on port 5001
    app.run(debug=True, port=5001)
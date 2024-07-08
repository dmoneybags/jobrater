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

TO DO:

load function, can be called when a user loads the app to grab all their data if not
initialized
'''

from flask import Flask, abort
from database_functions import DatabaseFunctions
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from mysql.connector.errors import IntegrityError
from auth_server import decode_user_from_token, token_required
#Set up our server using flask
app = Flask(__name__)
#Give support for cross origin requests from our content Script
CORS(app)

class DatabaseServer:
    #
    #
    # JOB METHODS
    #
    #
    @token_required
    @app.route('/databases/add_job', methods=['POST'])
    def add_job():
        token = request.headers.get('Authorization')
        userId = decode_user_from_token(token)["userId"]
        #Load the job data from the request, it is the the form of a string
        #so we load it into json using json.loads
        try:
            message = request.args.get('jobJson', default="NO JOB JSON LOADED", type=str)
            jobJson = json.loads(message)
            jobId = jobJson["jobId"]
        except json.JSONDecodeError:
            print("YOUR JOB JSON OF " + message + "IS INVALID")
            #Invalid request
            return abort(403)
        print("RECIEVED MESSAGE TO ADD JOB WITH ID " + jobJson["jobId"])
        #Call the database function to execute the insert
        try:
            response_code = DatabaseFunctions.add_user_job(userId, jobId)
        except:
            #its honestly ok if we try to read the same job a lot
            #client as of now doenst need to know an error occured
            return 'Already in User Job DB', 200
        try:
            #THIS ADDS THE JOB AND COMPANY AND KEYWORDS EACH TO THEIR
            #INDIVIDUAL TABLES
            response_code = DatabaseFunctions.add_job(jobJson)
            return response_code
        except IntegrityError:
            #its honestly ok if we try to read the same job a lot
            #client as of now doenst need to know an error occured
            return 'Already in DB', 200
    @app.route('/databases/read_most_recent_job', methods=['GET'])
    def read_most_recent_job():
        #Call the database function to select and sort to the most recent job
        result = DatabaseFunctions.read_most_recent_job()
        if not result:
            #Not found
            print(1, "DB IS EMPTY")
            abort(404)
        print("RETURNING RESULT")
        return result
    @app.route('/databases/read_job_by_id', methods=['GET'])
    def read_job_by_id():
        #Grab the jobId from the request, it is in the form of a string
        try:
            jobId = request.args.get('jobId', default="NO JOB ID LOADED", type=str)
        except:
            #invalid request
            print("Your request of: " + request)
            abort(403)
        print("JOB ID:  " + jobId)
        result = DatabaseFunctions.read_job_by_id(jobId)
        if not result:
            print("JOB NOT IN DB")
            abort(404)
        return result
    @app.route('/databases/update_job', methods=['POST'])
    def update_job():
        #We take an argument of the whole job data in the from a json string
        try:
            message = request.args.get('jobJson', default="NO JOB JSON LOADED", type=str)
            jobJson = json.loads(message)
        except json.JSONDecodeError:
            print("YOUR JOB JSON OF " + request + "IS INVALID")
            #Invalid request
            return abort(403)
        return DatabaseFunctions.update_job(jobJson)
    @app.route('/databases/delete_job', methods=['POST'])
    def delete_job():
        #Get the job id from the request
        try:
            jobId = request.args.get('jobId', default="NO JOB ID LOADED", type=str)
        except:
            print("Request of: " + request + " is invalid")
            #Invalid request
            return abort(403)
        #run the sql code
        return DatabaseFunctions.delete_job(jobId)
    #
    #
    # COMPANY METHODS
    #
    #
    #We only give the server an option to read companies,
    #theres no reason for us to make calls to update or delete companies yet
    @token_required
    @app.route('/databases/read_company', methods=["GET"])
    def read_company():
        try:
            company = request.args.get('company', default="NO COMPANY LOADED", type=str)
        except:
            print("Request of: " + request + " is invalid")
            #Invalid request
            return abort(403)
        print("Recieved message to read company: " + company)
        result = DatabaseFunctions.read_company_by_id(company)
        if not result:
            abort(404)
        return result
    #
    #
    # USER METHODS
    #
    #
    @token_required
    @app.route('/databases/get_user_data', methods=["GET"])
    #TO DO: ADD RETURNING JOBS
    def get_user_data():
        token = request.headers.get('Authorization')
        email = decode_user_from_token(token)["email"]
        user = DatabaseFunctions.read_user_by_email(email)
        if not user:
            abort(404)
        jobs = DatabaseFunctions.get_user_jobs()
        return jsonify({"user": user, "jobs": jobs})
    @app.route('/databases/get_user_by_googleId', methods=["GET"])
    def get_user_by_googleId():
        try:
            googleId = request.args.get('googleId', default="NO googleId LOADED", type=str)
        except:
            print("Request of: " + request + " is invalid")
            #Invalid request
            return abort(403)
        result = DatabaseFunctions.read_user_by_googleId(googleId)
        if not result:
            abort(404)
        return result
    @app.route('/databases/delete_user', methods=['POST'])
    def delete_user():
        token = request.headers.get('Authorization')
        user_email = decode_user_from_token(token)["email"]
        if not DatabaseFunctions.read_user_by_email(user_email):
            return jsonify({'message': 'User not in db'}), 401
        return DatabaseFunctions.delete_user(user_email)
if __name__ == '__main__':
    #Run the app on port 5001
    app.run(debug=True, port=5001)
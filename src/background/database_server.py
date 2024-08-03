'''
Execution flow:

Background.js

Listens for: a tab change event fired when the current tabs url changes
Executes: scrapes the jobId from the url
Sends: a message to the contentScript that we recieved a new job

ContentScript.js
Listens for: the new job event from background.js
Executes the scraping of the linkedin and glassdoor
Calls:

database_server.py
Listens for: requests sent on PORT 5001
Executes the database functions to CRUD jobs

TO DO:

load function, can be called when a user loads the app to grab all their data if not
initialized
'''

from flask import Flask, abort
from flask import Flask, request
from flask_cors import CORS
import json
from mysql.connector.errors import IntegrityError
from auth_logic import decode_user_from_token, token_required
from job_location_table import JobLocationTable
from user_job_table import UserJobTable
from user_table import UserTable
from job_table import JobTable
from company_table import CompanyTable
from resume_table import ResumeTable
from resume_nlp.resume_comparison import ResumeComparison
from company import Company
from job import Job
from user import User
from resume import Resume
from typing import Dict
import glassdoor_scraper
from helper_functions import HelperFunctions
import daemon
import sys
import os
import traceback
import asyncio
import signal
from functools import partial

signal.signal(signal.SIGTERM, partial(HelperFunctions.handle_sigterm, caller_name="database_server"))

#Set up our server using flask
app = Flask(__name__)
#Give support for cross origin requests from our content Script
CORS(app)
PORT=5001

CANSCRAPEGLASSDOOR: bool = True

class DatabaseServer:
    #
    #
    # JOB METHODS
    #
    #
    '''
    add_job

    recieves the request to add a job and executes the request
        request
            token: str token of the users auth
    
    returns Response
    '''
    @app.route('/databases/add_job', methods=['POST'])
    @token_required
    def add_job():
        print("=============== BEGIN ADD JOB =================")
        async def get_company_data_async(company: str) -> Dict:
            return await glassdoor_scraper.get_company_data(company)

        token : str = request.headers.get('Authorization')
        user : User | None = decode_user_from_token(token)
        if not user:
            return "NO TOKEN SENT", 401
        user_id : str = user.user_id
        try:
            message : str = request.args.get('jobJson', default="NO JOB JSON LOADED", type=str)
            job_json : Dict = json.loads(message)
            print("=============== RECIEVED JOB JSON OF =========== \n\n")
            print(json.dumps(job_json, indent=4))
            companyName: str = job_json["company"]["companyName"]
            if (not CompanyTable.read_company_by_id("company") and CANSCRAPEGLASSDOOR):
                print("RETRIEVING COMPANY FROM GLASSDOOR")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                job_json["company"] = loop.run_until_complete(get_company_data_async(companyName))
            print("\n\n")
        except json.JSONDecodeError:
            print("YOUR JOB JSON OF " + message + "IS INVALID")
            #Invalid request
            return abort(403)
        print(job_json)
        job : Job = Job.create_with_json(job_json)
        print("RECIEVED MESSAGE TO ADD JOB WITH ID " + job_json["jobId"])
        #Call the database function to execute the insert
        #we complete the jobs data before returning it to the client
        completeJob: Job = JobTable.add_job_with_foreign_keys(job, user_id)
        assert(completeJob.company is not None)
        print("============== END ADD JOB ================")
        return json.dumps({"job": completeJob.to_json()}), 200
    '''
    read_most_recent_job

    reads the most recently added job from the db

    args:
        None
    returns:
        json representation of job
    '''
    @app.route('/databases/read_most_recent_job', methods=['GET'])
    @token_required
    def read_most_recent_job():
        #Call the database function to select and sort to the most recent job
        job : Job | None = JobTable.read_most_recent_job()
        if not job:
            #Not found
            print("DB IS EMPTY")
            abort(404)
        print("RETURNING RESULT")
        return job.to_json()
    '''
    read_job_by_id

    recieves request to read a company by the companies str id and returns the json representation of the job 

    args:
        request
            job_id str job id from linkedin
    returns:
        json representation of job
    '''
    @app.route('/databases/read_job_by_id', methods=['GET'])
    @token_required
    def read_job_by_id():
        #Grab the jobId from the request, it is in the form of a string
        try:
            job_id : str = request.args.get('jobId', default="NO JOB ID LOADED", type=str)
        except:
            #invalid request
            print("Your request of: " + request)
            abort(403)
        print("JOB ID:  " + job_id)
        job : Job | None = JobTable.read_job_by_id(job_id)
        if not job:
            print("JOB NOT IN DB")
            abort(404)
        return job.to_json()
    '''
    update_job

    recieves request to update company

    args:
        request
            jobJson the json of the job to set the job to
    returns:
        response message and code
    '''
    @app.route('/databases/update_job', methods=['POST'])
    @token_required
    def update_job():
        #We take an argument of the whole job data in the from a json string
        try:
            message : str = request.args.get('jobJson', default="NO JOB JSON LOADED", type=str)
            job_json : Dict = json.loads(message)
            job : Job = Job.create_with_json(job_json)
        except json.JSONDecodeError:
            print("YOUR JOB JSON OF " + request + "IS INVALID")
            #Invalid request
            return abort(403)
        JobTable.update_job(job)
        return 'success', 200
    '''
    delete_job

    recieves request to delete company

    args:
        request
            job_id the id of the job to delete
    returns:
        response message and code
    '''
    @app.route('/databases/delete_job', methods=['POST'])
    @token_required
    def delete_job():
        #Get the job id from the request
        try:
            job_id : str = request.args.get('jobId', default="NO JOB ID LOADED", type=str)
        except:
            print("Request of: " + request + " is invalid")
            #Invalid request
            return abort(403)
        #run the sql code
        JobTable.delete_job_by_id(job_id)
        return 'success', 200
    #
    #
    # COMPANY METHODS
    #
    #
    #We only give the server an option to read companies,
    #theres no reason for us to make calls to update or delete companies yet
    '''
    read_company_by_name

    responds to request and gets a companys data by name

    args:
        request
            company: str company name
    returns
        company json
    '''
    @app.route('/databases/read_company', methods=["GET"])
    @token_required
    def read_company_by_name():
        try:
            company : str = request.args.get('company', default="NO COMPANY LOADED", type=str)
        except:
            print("Request of: " + request + " is invalid")
            #Invalid request
            return abort(403)
        print("Recieved message to read company: " + company)
        company : Company | None = CompanyTable.read_company_by_id(company)
        if not company:
            abort(404)
        return company.to_json()
    #
    #
    # USER METHODS
    #
    #
    '''
    get_user_data

    responds to a request to retrive the users data from the dbs

    for now just:
        user columns
        user jobs
    
    args:
        request
            token: JWT token that holds user id
    returns:
        json with user data and job data
    '''
    @app.route('/databases/get_user_data', methods=["GET"])
    @token_required
    def get_user_data():
        token : str = request.headers.get('Authorization')
        if not token:
            return 'No token recieved', 401
        user : User | None = decode_user_from_token(token)
        if not user:
            abort(404)
        jobs : list[Job] = UserJobTable.get_user_jobs(user.user_id)
        resumes: list[Resume] = ResumeTable.read_user_resumes(user.user_id)
        json_jobs : list[Dict] = [job.to_json() for job in jobs]
        json_resumes : list[Dict] = [resume.to_json() for resume in resumes]
        return json.dumps({"user": user.to_json(), "jobs": json_jobs, "resumes": json_resumes})
    '''
    get_user_data_by_googleId

    grabs a users data using their google id instead of their token

    no implementation yet

    args:
        request
            googleId: the google id of the user as a str
    returns:
        json with user data and job data
    '''
    #Should this require token? what is the implementation
    @app.route('/databases/get_user_by_googleId', methods=["GET"])
    @token_required
    def get_user_data_by_googleId():
        try:
            googleId : str = request.args.get('googleId', default="NO googleId LOADED", type=str)
        except:
            print("Request of: " + request + " is invalid")
            #Invalid request
            return abort(403)
        user : User | None = UserTable.read_user_by_googleId(googleId)
        if not user:
            abort(404)
        jobs : list[Job] = UserJobTable.get_user_jobs(user["userId"])
        json_jobs : list[Dict] = [job.to_json() for job in jobs]
        return json.dumps({"user": user.to_json(), "jobs": json_jobs})
    '''
    delete_user

    deletes a user using the token passed in the request

    args:
        request
            token: jwt auth token
    returns:
        success message or error
    '''
    @app.route('/databases/delete_user', methods=['POST'])
    @token_required
    def delete_user():
        token : str = request.headers.get('Authorization')
        if not token:
            return 'No token recieved', 401
        user : User | None = decode_user_from_token(token)
        if not user:
            return 'Invalid Token', 401
        user_email : str = user.email
        if not UserTable.read_user_by_email(user_email):
            return json.dumps({'message': 'User not in db'}), 401
        UserTable.delete_user_by_email(user_email)
        return 'success', 200
    #
    #
    # RESUME METHODS
    #
    #
    @app.route('/databases/add_resume', methods=['POST'])
    @token_required
    def add_resume():
        token : str = request.headers.get('Authorization')
        user : User | None = decode_user_from_token(token)
        resume_json_str: str = request.args.get('resume', default="NO RESUME LOADED", type=str)
        resume: Resume = Resume.create_with_json(json.loads(resume_json_str))
        ResumeTable.add_resume(user.user_id, resume)
        return 'success', 200
    @app.route('/databases/delete_resume', methods=['POST'])
    @token_required
    def delete_resume():
        resume_id: str = request.args.get('resumeId', default="NO RESUME LOADED", type=str)
        ResumeTable.delete_resume(resume_id)
        return 'success', 200
    @app.route('/databases/compare_resumes', methods=['GET'])
    @token_required
    def compare_resumes():
        token : str = request.headers.get('Authorization')
        user : User | None = decode_user_from_token(token)
        job_description: str = request.args.get('jobDescription', default="NO JOB DESCRIPTION LOADED", type=str)
        resumes: list[Resume] = ResumeTable.read_user_resumes(user.user_id)
        resume_comparison_data: Dict = {}
        for resume in resumes:
            similarity_matrix = ResumeComparison.get_similarity_matrix(job_description, resume)
            sorted_index_list = ResumeComparison.compare_embeddings(similarity_matrix)
            resume_comparison_data[resume.id] = {
                "similarityMatrix": ResumeComparison.serialize_similarity_matrix(similarity_matrix),
                "sortedIndexList": ResumeComparison.serialize_similarity_matrix(sorted_index_list)
            }
        return json.dumps(resume_comparison_data) 
    '''
    run_as_daemon

    runs our server as a daemon
    '''
    def run_as_daemon():
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        stdout_path = os.path.join(log_dir, 'database_server.stdout')
        stderr_path = os.path.join(log_dir, 'database_server.stderr')

        #Run the app on port 5001
        try:
            # Open files for stdout and stderr
            # Set up the DaemonContext with redirected stdout and stderr
            print("STARTING DAEMON IN " + os.getcwd())
            with daemon.DaemonContext(
                working_directory=os.getcwd(),
                stdout = open(stdout_path, "w+"),
                stderr = open(stderr_path, "w+")
            ):
                HelperFunctions.write_pid_to_temp_file("database_server")
                app.run(debug=False, port=PORT)
        except Exception as e:
            print(e)
            traceback.print_exc()
if __name__ == '__main__':
    # Check for the -I argument
    if '-i' in sys.argv:
        # Run the script normally without daemonizing
        print("Running in non-daemon mode")
        app.run(debug=False, port=PORT)
    else:
        DatabaseServer.run_as_daemon()
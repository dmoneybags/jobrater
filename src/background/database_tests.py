import json
from database_functions import DatabaseFunctions
import mysql.connector
import os
import subprocess
from auth_server import decode_user_from_token, get_token

#TESTS JUST DB CODE, NO SERVERS
job_data = {
    "company": "Apple",
    "job": "Specification Sales",
    "keywords": [
        "sales",
        "commercial",
        "experience",
        "development",
        "new",
        "specification",
        "executive",
        "channel",
        "residential",
        "000",
        "uncapped",
        "commission",
        "wow",
        "industry",
        "product",
        "space"
    ],
    "location": "Cupertino, CA",
    "secondsPostedAgo": 1814400,
    "applicants": "100",
    "paymentFreq": "yr",
    "paymentBase": 90,
    "paymentHigh": 110,
    "mode": "Hybrid",
    "careerStage": "Mid-Senior level",
    "jobId": "3936196442",
    "businessOutlookRating": 1,
    "careerOpportunitiesRating": 5,
    "ceoRating": 1,
    "compensationAndBenefitsRating": 5,
    "cultureAndValuesRating": 5,
    "diversityAndInclusionRating": 5,
    "overallRating": 5,
    "seniorManagementRating": 5,
    "workLifeBalanceRating": 4.7
}
def user_tests():
    print("TESTING USER CODE")
    salt = 0
    user = {
        "email": "dandemoney@gmail.com",
        "password": "RockyRaccoon1996",
        "name": "Daniel DeMoney",
        "location": "112 Adrian Pl"
    }
    print("TESTING ADDING USER")
    DatabaseFunctions.add_user(user, salt)
    print("TESTING READING USER")
    read_user = json.loads(DatabaseFunctions.read_user_by_email(user["email"]))
    print("Read user " + json.dumps(read_user))
    print("Original user " + json.dumps(user))
    assert(user["email"] == read_user["email"])
    assert(user["name"] == read_user["name"])
    assert(user["location"] == read_user["location"])
    print("USER SUCCESSFULLY REREAD")
    print("TESTING DELETE USER")
    DatabaseFunctions.delete_user(user["email"])
    assert(not DatabaseFunctions.read_user_by_email(user["email"]))
    print("SUCCESSFULLY DELETED USER")
    print("READDING USER FOR TESTS")
    DatabaseFunctions.add_user(user, salt)
    read_user = json.loads(DatabaseFunctions.read_user_by_email(user["email"]))
    return read_user["userID"]
def company_tests():
    print("TESTING COMPANY CODE")
    print("TESTING ADDING COMPANY")
    DatabaseFunctions.add_company(job_data)
    print("COMPANY ADDED SUCCESSFULLY")
    print("ATTEMPTING TO READ COMPANY")
    print("COMPANY DATA READ:" + DatabaseFunctions.read_company_by_id("Apple"))
    print("COMPANY READ")
    print("ATTEMPTING TO UPDATE COMPANY")
    DatabaseFunctions.update_company({"company": "Apple", "ceoRating": 4.8})
    company_query = json.loads(DatabaseFunctions.read_company_by_id("Apple"))
    assert(company_query["ceoRating"] == "4.80")
    print("SUCCESSFULLY READ COMPANY AFTER UPDATE")
    DatabaseFunctions.delete_company("Apple")
    assert(not DatabaseFunctions.read_company_by_id("Apple"))
    print("SUCCESSFULLY DELETED COMPANY")
def job_tests(user_id):
    print("TESTING ADDING JOB WITHOUT COMPANY IN DB")
    print(user_id)
    DatabaseFunctions.add_job(job_data, user_id)
    #assert that the company correctly loaded
    assert(DatabaseFunctions.read_company_by_id("Apple") is not None)
    assert(DatabaseFunctions.read_job_by_id(job_data["jobId"]) is not None)
    print("SUCCESSFULLY ADDED JOB WITH A NEW COMPANY")
    print("TESTING DELETING JOBS")
    DatabaseFunctions.delete_job(job_data["jobId"])
    assert(DatabaseFunctions.read_company_by_id("Apple") is not None)
    print("COMPANY LOGIC SUCEEDED")
    print("READDING JOB SUCEEDED")
def user_job_tests(user_id):
    print("BEGINNNING USER JOB TESTS")
    print("TESTING READING BACK USER JOBS AFTER ADDING")
    job_strs = ["Application Programmer", "Janitor", "CSM (In person ONLY!)", "Professional Dookier (SENIOR LEVEL)"]
    job_id = ["1835781350", "3252359832", "2335285392", "3295295725"]
    for i in range(len(job_strs)):
        job_data_copy = job_data
        job_data_copy["job"] = job_strs[i]
        job_data_copy["jobId"] = job_id[i]
        print("TEST JOB BEING ADDED WITH NAME " + job_strs[i])
        DatabaseFunctions.add_job(job_data_copy, user_id)
    results = json.loads(DatabaseFunctions.get_user_jobs(user_id))
    print(results)
    assert(len(results) == len(job_strs))
    for result in results:
        #make sure the title is in our list
        assert(job_strs.count(result["job"]) == 1)
    print("USER JOBS SUCCESSFULLy READ")
    #test that deleting the job deletes the user job
    #double adds
    #test that deleting the user job does NOT delete the job



    
    
if __name__ == "__main__":
    user_id = user_tests()
    company_tests()
    job_tests(user_id)
    user_job_tests(user_id)


    
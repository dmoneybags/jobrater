import json
from database_functions import DatabaseFunctions
import mysql.connector
import os
import subprocess

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
if __name__ == "__main__":
    DatabaseFunctions.run_sql_file(os.getcwd() + "/src/background/CreateDB.sql")
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
    print("TESTING ADDING JOB WITHOUT COMPANY IN DB")
    DatabaseFunctions.add_job(job_data)
    #assert that the company correctly loaded
    assert(DatabaseFunctions.read_company_by_id("Apple") is not None)
    assert(DatabaseFunctions.read_job_by_id(job_data["jobId"]) is not None)
    print("SUCCESSFULLY ADDED JOB WITH A NEW COMPANY")
    print("TESTING DELETING JOBS")
    DatabaseFunctions.delete_job(job_data["jobId"])
    assert(DatabaseFunctions.read_company_by_id("Apple") is not None)
    print("COMPANY LOGIC SUCEEDED")
    DatabaseFunctions.add_job(job_data)
    print("READDING JOB SUCEEDED")
    
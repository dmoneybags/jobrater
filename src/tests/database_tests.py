import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'background')))

import json
from auth_logic import decode_user_from_token, get_token
from uuid import uuid1
from user_table import UserTable
from user import User
from company import Company
from company_table import CompanyTable
from job import Job
from job_table import JobTable
from user_job_table import UserJobTable


#TESTS JUST DB CODE, NO SERVERS
job_data = {
    "job": "Specification Sales",
    "locationStr": "Cupertino, CA",
    "secondsPostedAgo": 1814400,
    "applicants": "100",
    "paymentFreq": "yr",
    "paymentBase": 90,
    "paymentHigh": 110,
    "mode": "Hybrid",
    "careerStage": "Mid-Senior level",
    "jobId": "3936196442",
    "company": {
        "companyName": "Apple",
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
}
def user_tests():
    print("TESTING USER CODE")

    user_json = {
        "userId": str(uuid1()),
        "email": "dandemoney@gmail.com",
        "password": "Xdfgh1012",
        "firstName": "Daniel",
        "lastName": "DeMoney",
        "salt": "!#%!%!%!#%!",
        "googleId": None,

    }
    user = User.create_with_json(user_json)

    print("TESTING ADDING USER")
    UserTable.add_user(user)
    print("SUCEEDED READING USER BACK \n \n")

    print("TESTING READING USER")
    read_user = UserTable.read_user_by_email(user.email)
    assert(user.email == read_user.email)
    assert(user.first_name == read_user.first_name)
    assert(user.last_name == read_user.last_name)
    assert(user.password == read_user.password)
    assert(str(user.user_id) == str(read_user.user_id))
    print("SUCEEDED READING USER BACK \n \n")

    print("TESTING DUMPING USER OBJECT TO JSON")
    read_user_json = read_user.to_json()
    print("Read user " + json.dumps(read_user_json))
    print("Original user " + json.dumps(user_json))
    assert(user_json["email"] == read_user_json["email"])
    assert(user_json["firstName"] == read_user_json["firstName"])
    assert(user_json["lastName"] == read_user_json["lastName"])
    assert(user_json["password"] == read_user_json["password"])
    assert(user_json["userId"] == read_user_json["userId"])
    print("USER SUCCESSFULLY DUMPED TO JSON \n \n")

    print("TESTING DELETE USER")
    UserTable.delete_user_by_email(user_json["email"])
    assert(not UserTable.read_user_by_email(user_json["email"]))
    print("SUCCESSFULLY DELETED USER \n \n")

    print("READDING USER FOR TESTS")
    UserTable.add_user(user)
    read_user = UserTable.read_user_by_email(user.email)
    return read_user.user_id

def company_tests():
    print("TESTING COMPANY CODE \n\n")
    print("TESTING ADDING COMPANY")
    company = Company.create_with_json(job_data["company"])
    CompanyTable.add_company(company)
    print("COMPANY ADDED SUCCESSFULLY \n\n")

    print("ATTEMPTING TO READ COMPANY")
    read_company = CompanyTable.read_company_by_id("Apple")
    print("COMPANY DATA READ:" + json.dumps(read_company.to_json()))
    assert(read_company.business_outlook_rating == job_data["company"]["businessOutlookRating"])
    assert(read_company.career_opportunities_rating == job_data["company"]["careerOpportunitiesRating"])
    assert(read_company.compensation_and_benefits_rating == job_data["company"]["compensationAndBenefitsRating"])
    assert(read_company.culture_and_values_rating == job_data["company"]["cultureAndValuesRating"])
    assert(read_company.diversity_and_inclusion_rating == job_data["company"]["diversityAndInclusionRating"])
    assert(read_company.overall_rating == job_data["company"]["overallRating"])
    print("COMPANY READ \n\n")

    print("ATTEMPTING TO UPDATE COMPANY")
    update_json = job_data["company"]
    update_json["ceoRating"] = 4.8
    CompanyTable.update_company(Company.create_with_json(update_json))
    reread_company = CompanyTable.read_company_by_id("Apple")
    assert(float(reread_company.ceo_rating) == 4.8)
    print("SUCCESSFULLY READ COMPANY AFTER UPDATE \n\n")

    print("TESTING DELETE COMPANY")
    CompanyTable.delete_company_by_name("Apple")
    assert(not CompanyTable.read_company_by_id("Apple"))
    print("SUCCESSFULLY DELETED COMPANY \n\n")

    print("========== PASSED COMPANY TESTS =========== \n\n")

def job_tests(user_id):
    print("TESTING ADDING JOB WITHOUT COMPANY IN DB")
    print(user_id)
    job = Job.create_with_json(job_data)
    JobTable.add_job_with_foreign_keys(job, user_id)
    #assert that the company correctly loaded
    assert(CompanyTable.read_company_by_id("Apple") is not None)
    assert(JobTable.read_job_by_id(job_data["jobId"]) is not None)
    print("SUCCESSFULLY ADDED JOB WITH A NEW COMPANY \n\n")

    print("TESTING DELETING JOBS")
    JobTable.delete_job_by_id(job_data["jobId"])
    assert(CompanyTable.read_company_by_id("Apple") is not None)
    print("COMPANY LOGIC SUCEEDED \n\n")
    print("READING JOB SUCEEDED \n\n")

    print("========== PASSED COMPANY TESTS =========== \n\n")

def user_job_tests(user_id):
    print("BEGINNNING USER JOB TESTS \n\n")
    print("TESTING READING BACK USER JOBS AFTER ADDING")
    job_strs = ["Application Programmer", "Janitor", "CSM (In person ONLY!)", "Professional Dookier (SENIOR LEVEL)"]
    job_id = ["1835781350", "3252359832", "2335285392", "3295295725"]
    for i in range(len(job_strs)):
        job_data_copy = job_data
        job_data_copy["job"] = job_strs[i]
        job_data_copy["jobId"] = job_id[i]
        print("TEST JOB BEING ADDED WITH NAME " + job_strs[i])
        job = Job.create_with_json(job_data_copy)
        JobTable.add_job_with_foreign_keys(job, user_id)
    results = UserJobTable.get_user_jobs(user_id)
    print(results)
    assert(len(results) == len(job_strs))
    for result in results:
        #make sure the title is in our list
        assert(job_strs.count(result.job_name) == 1)
    print("USER JOBS SUCCESSFULLY READ")
    #test that deleting the job deletes the user job
    print("TESTING DELETING JOB AND READING USER JOB")
    JobTable.delete_job_by_id(job_id[2])
    results = UserJobTable.get_user_jobs(user_id)
    for result in results:
        assert(result.job_id != job_id[2])
    print("USER JOB SUCCESSFULLY DELETED \n\n")
    #double adds
    print("ATTEMPTING TO DOUBLE ADD A USER JOB")
    job_data_copy = job_data
    job_data_copy["jobId"] = job_id[0]
    JobTable.add_job_with_foreign_keys(Job.create_with_json(job_data_copy), user_id)
    #test that deleting the user job does NOT delete the job
    print("TESTING THAT JOB PERSISTS WHEN USER JOB IS DELETED")
    UserJobTable.delete_user_job(user_id, job_id[0])
    job = JobTable.read_job_by_id(job_id[0])
    assert(job.company.company_name == "Apple")
    print("JOB PERSISTS TEST PASSED \n\n")

if __name__ == "__main__":
    user_id = user_tests()
    company_tests()
    job_tests(user_id)
    user_job_tests(user_id)


    
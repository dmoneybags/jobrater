from mysql.connector.types import RowType, RowItemType
from typing import Dict
from decimal import Decimal
from typing import Optional

class CompanyInvalidData(Exception):
        def __init__(self, data: any, message : str ="INVALID DATA PASSED TO CONSTRUCTOR"):
            self.message = message + " DATA RECIEVED: " + str(data)
            super().__init__(self.message)

class Company:
    '''
    __init__

    creates a company object when given all the appropriate values

    args:
        company name: string company name
        business_outlook_rating: from glassdoor, 1 decimal point decimal
        career_opportunities_rating: from glassdoor, 1 decimal point decimal
        ceo_rating: from glassdoor, 1 decimal point decimal
        compensation_and_benefits_rating: from glassdoor, 1 decimal point decimal
        senior_management_rating: from glassdoor 1 decimal point decimal
        work_life_balance_rating: from glassdoor 1 decimal point decimal
        overall_rating: from glassdoor 1 decimal point decimal
    returns
        initialized company object
    '''
    def __init__(self, company_name : str, business_outlook_rating : Decimal, career_opportunities_rating : Decimal, ceo_rating : Decimal, 
                 compensation_and_benefits_rating : Decimal, culture_and_values_rating : Decimal, diversity_and_inclusion_rating : Decimal, senior_management_rating : Decimal, 
                 work_life_balance_rating : Decimal, overall_rating : Decimal) -> None:
        self.company_name : str = company_name
        self.business_outlook_rating : Decimal = business_outlook_rating
        self.career_opportunities_rating : Decimal = career_opportunities_rating
        self.ceo_rating : Decimal = ceo_rating
        self.compensation_and_benefits_rating : Decimal = compensation_and_benefits_rating
        self.culture_and_values_rating : Decimal = culture_and_values_rating
        self.diversity_and_inclusion_rating : Decimal = diversity_and_inclusion_rating
        self.senior_management_rating : Decimal = senior_management_rating
        self.work_life_balance_rating : Decimal = work_life_balance_rating
        self.overall_rating : Decimal = overall_rating
    '''
    create_with_sql_row

    returns a company object when passed a sql row returned from query.fetchone

    args:
        sql_query_row: result of query fetchone with dictionary=True
    returns:
        Company object
    '''
    @classmethod
    def create_with_sql_row(cls, sql_query_row: (Dict[str, RowItemType])) -> 'Company':
        company_name : str
        business_outlook_rating : Decimal 
        career_opportunities_rating : Decimal
        ceo_rating : Decimal
        compensation_and_benefits_rating : Decimal
        culture_and_values_rating : Decimal
        diversity_and_inclusion_rating : Decimal
        senior_management_rating : Decimal
        work_life_balance_rating : Decimal
        overall_rating : Decimal
        try:
            company_name = sql_query_row["CompanyName"]
            business_outlook_rating = sql_query_row["BusinessOutlookRating"]
            career_opportunities_rating = sql_query_row["CareerOpportunitiesRating"]
            ceo_rating = sql_query_row["CeoRating"]
            compensation_and_benefits_rating = sql_query_row["CompensationAndBenefitsRating"]
            culture_and_values_rating = sql_query_row["CultureAndValuesRating"]
            diversity_and_inclusion_rating = sql_query_row["DiversityAndInclusionRating"]
            senior_management_rating = sql_query_row["SeniorManagementRating"]
            work_life_balance_rating = sql_query_row["WorkLifeBalanceRating"]
            overall_rating = sql_query_row["OverallRating"]
            return cls(company_name, business_outlook_rating, career_opportunities_rating, ceo_rating, compensation_and_benefits_rating , culture_and_values_rating, diversity_and_inclusion_rating,
                       senior_management_rating, work_life_balance_rating, overall_rating)
        except KeyError as e:
            print(f"FAILED TO CREATE COMPANY RECIEVED KEYERROR OF {e}")
            raise CompanyInvalidData(sql_query_row)
    '''
    try_create_with_sql_row

    returns a company object if it is included in the sql row, if not returns None

    args:
        sql_query_row: result of query fetchone with dictionary=True
    returns:
        Company object OR None
    '''
    @classmethod
    def try_create_with_sql_row(cls, sql_query_row: (Dict[str, RowItemType])) -> Optional['Company']:
        company_name : str
        business_outlook_rating : Decimal 
        career_opportunities_rating : Decimal
        ceo_rating : Decimal
        compensation_and_benefits_rating : Decimal
        culture_and_values_rating : Decimal
        diversity_and_inclusion_rating : Decimal
        senior_management_rating : Decimal
        work_life_balance_rating : Decimal
        overall_rating : Decimal
        try:
            company_name = sql_query_row["CompanyName"]
            business_outlook_rating = sql_query_row["BusinessOutlookRating"]
            career_opportunities_rating = sql_query_row["CareerOpportunitiesRating"]
            ceo_rating = sql_query_row["CeoRating"]
            compensation_and_benefits_rating = sql_query_row["CompensationAndBenefitsRating"]
            culture_and_values_rating = sql_query_row["CultureAndValuesRating"]
            diversity_and_inclusion_rating = sql_query_row["DiversityAndInclusionRating"]
            senior_management_rating = sql_query_row["SeniorManagementRating"]
            work_life_balance_rating = sql_query_row["WorkLifeBalanceRating"]
            overall_rating = sql_query_row["OverallRating"]
            return cls(company_name, business_outlook_rating, career_opportunities_rating, ceo_rating, compensation_and_benefits_rating , culture_and_values_rating, diversity_and_inclusion_rating,
                       senior_management_rating, work_life_balance_rating, overall_rating)
        except KeyError as e:
            print(f"FAILED TO CREATE COMPANY RECIEVED KEYERROR OF {e}")
            print("Returning empty company")
            return None
    '''
    create_with_json

    returns a company object when passed json containing the keys for the company values

    args:
        request_json: built to take the return of the python glassdoor scraper
    returns:
        Company object
    '''
    @classmethod
    def create_with_json(cls, request_json: Dict) -> 'Company':
        company_name : str
        business_outlook_rating : Decimal 
        career_opportunities_rating : Decimal
        ceo_rating : Decimal
        compensation_and_benefits_rating : Decimal
        culture_and_values_rating : Decimal
        diversity_and_inclusion_rating : Decimal
        senior_management_rating : Decimal
        work_life_balance_rating : Decimal
        overall_rating : Decimal
        try:
            company_name = request_json["companyName"]
            business_outlook_rating = request_json["businessOutlookRating"]
            career_opportunities_rating = request_json["careerOpportunitiesRating"]
            ceo_rating = request_json["ceoRating"]
            compensation_and_benefits_rating = request_json["compensationAndBenefitsRating"]
            culture_and_values_rating = request_json["cultureAndValuesRating"]
            diversity_and_inclusion_rating = request_json["diversityAndInclusionRating"]
            senior_management_rating = request_json["seniorManagementRating"]
            work_life_balance_rating = request_json["workLifeBalanceRating"]
            overall_rating = request_json["overallRating"]
            return cls(company_name, business_outlook_rating, career_opportunities_rating, ceo_rating, compensation_and_benefits_rating , culture_and_values_rating, diversity_and_inclusion_rating,
                       senior_management_rating, work_life_balance_rating, overall_rating)
        except KeyError:
            raise CompanyInvalidData(request_json)
    '''
    create_with_json

    tries to returns a company object when passed json will return none if the keys aren't present

    args:
        request_json: built to take the return of the python glassdoor scraper
    returns:
        Company object or None
    '''
    @classmethod
    def try_create_with_json(cls, request_json: Dict) -> 'Company':
        company_name : str
        business_outlook_rating : Decimal 
        career_opportunities_rating : Decimal
        ceo_rating : Decimal
        compensation_and_benefits_rating : Decimal
        culture_and_values_rating : Decimal
        diversity_and_inclusion_rating : Decimal
        senior_management_rating : Decimal
        work_life_balance_rating : Decimal
        overall_rating : Decimal
        try:
            company_name = request_json["companyName"]
            business_outlook_rating = request_json["businessOutlookRating"]
            career_opportunities_rating = request_json["careerOpportunitiesRating"]
            ceo_rating = request_json["ceoRating"]
            compensation_and_benefits_rating = request_json["compensationAndBenefitsRating"]
            culture_and_values_rating = request_json["cultureAndValuesRating"]
            diversity_and_inclusion_rating = request_json["diversityAndInclusionRating"]
            senior_management_rating = request_json["seniorManagementRating"]
            work_life_balance_rating = request_json["workLifeBalanceRating"]
            overall_rating = request_json["overallRating"]
            return cls(company_name, business_outlook_rating, career_opportunities_rating, ceo_rating, compensation_and_benefits_rating , culture_and_values_rating, diversity_and_inclusion_rating,
                       senior_management_rating, work_life_balance_rating, overall_rating)
        except KeyError as e:
            print(f"FAILED TO CREATE COMPANY RECIEVED KEYERROR OF {e}")
            print("Returning empty company")
            return cls(company_name, 0, 0, 0, 0 , 0, 0, 0, 0, 0)
    '''
    to_json

    converts company object to json

    args:
        None
    returns:
        json dict
    '''
    def to_json(self) -> Dict:
        return {
            "companyName" : self.company_name,
            "businessOutlookRating" : str(self.business_outlook_rating),
            "careerOpportunitiesRating" : str(self.career_opportunities_rating),
            "ceoRating" : str(self.ceo_rating),
            "compensationAndBenefitsRating" : str(self.compensation_and_benefits_rating),
            "cultureAndValuesRating" : str(self.culture_and_values_rating),
            "diversityAndInclusionRating" : str(self.diversity_and_inclusion_rating),
            "seniorManagementRating" : str(self.senior_management_rating),
            "workLifeBalanceRating" : str(self.work_life_balance_rating),
            "overallRating" : str(self.overall_rating)
        }
    '''
    isEmpty

    returns whether or not a company object is empty

    args:
        self
    returns:
        isEmpty: bool whether or not its empty
    '''
    def isEmpty(self):
        values: list[Decimal] = [self.business_outlook_rating, self.career_opportunities_rating, self.ceo_rating, self.compensation_and_benefits_rating, self.culture_and_values_rating, self.diversity_and_inclusion_rating, self.senior_management_rating, self.work_life_balance_rating]
        try:
            return sum(values) == 0
        except TypeError:
            return True
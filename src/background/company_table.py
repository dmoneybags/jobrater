from database_functions import DatabaseFunctions
import json
from collections import OrderedDict
from typing import Dict
from company import Company
from mysql.connector.cursor import MySQLCursor
from mysql.connector.types import RowType, RowItemType


class CompanyTable:
    '''
    __get_company_add_query

    gets the query to add a company to db

    args:
        company_json: lets us know the cols the job has valid data in
    returns:
        str sql query with %s for replacement
    '''
    def __get_company_add_query(company_json : Dict) -> str:
        cols : list[str] = list(company_json.keys())
        col_str : str = ", ".join(cols)
        #Creates a comma separated of %s characters for string replacement when we run the 
        #query
        vals : str = ", ".join(["%s"] * len(cols))
        return f"INSERT INTO Company ({col_str}) VALUES ({vals})"
    '''
    __get_update_str_company

    gets str sql query to update company in db. Again takes company_json so we know what cols

    args:
        company_json: json representation of company (dict) [col:value]
    returns:
        sql query with %s for replacement
    '''
    def __get_update_str_company(company_json : Dict) -> str:
        cols : list[str] = list(company_json.keys())
        #name needs to ba at the end, lets pop it right now
        _ = cols.pop(0)
        col_str : str = "=%s, ".join(cols)
        #add on last replacement str
        col_str = col_str + "=%s"
        update_str : str = f"UPDATE Company SET {col_str} WHERE CompanyName = %s"
        return update_str
    '''
    __get_delete_company_by_name_query

    gets query to delete a company by name from db

    returns:
        query with %s for replacement
    '''
    def __get_delete_company_by_name_query() -> str:
        return f"DELETE FROM Company WHERE CompanyName=%s"
    '''
    __get_read_company_by_name_query

    gets query to read a company by name

    returns:
        query with %s for replacement
    '''
    def __get_read_company_by_name_query() -> str:
        return """
            SELECT *
            FROM Company
            WHERE CompanyName = %s;
        """
    '''
    add_company

    adds a company object to our sql db

    args:
        company: Company type company object
    returns:
        0 if no errors occured
    '''
    def add_company(company : Company) -> int:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        cursor.execute("USE JOBDB")
        company_json : Dict = company.to_json()
        company_add_str : str = CompanyTable.__get_company_add_query(company_json)
        cursor.execute(company_add_str, list(company_json.values()))
        print("COMPANY SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
    '''
    read_company_by_id

    reads a company by id (currently name) from our db and returns the company object

    args: 
        company_name: str company name
    returns:
        Company object if found or None
    '''
    def read_company_by_id(company_name : str) -> Company | None:
        #put in try except, return custom error if doesn't work
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        query : str = CompanyTable.__get_read_company_by_name_query()
        cursor.execute("USE JOBDB")
        cursor.execute(query, (company_name,))
        result : Dict[str, RowItemType] = cursor.fetchone()
        print(result)
        if not result or None in result:
            return None
        cursor.close()
        return Company.create_with_sql_row(result)
    '''
    update_company

    updates a company in our db, the company object passed has all values corresponding to its name overwritten
    in db

    args: 
        company: Company object to update
    returns:
        0 if no errors occurred
    '''
    def update_company(company : Company) -> int:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        company_json : Dict = company.to_json()
        print("RECIEVED MESSAGE TO UPDATE Company WITH ID " + company_json["companyName"])
        #Grab the specific update columns to add to our query
        update : str = CompanyTable.__get_update_str_company(company_json)
        #convert the values of our json to a list
        #Our list will retain order
        params = list(company_json.values())
        #company name needs to be last for the where clause
        _ = params.pop(0)
        params.append(company_json["companyName"])
        cursor.execute("USE JOBDB")
        #Execute the query
        print(update)
        print(params)
        cursor.execute(update, params)
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        #return success
        return 0
    '''
    delete_company_by_name

    deletes a company in our db, matched to the name passed

    args: 
        company_name: company by name to delete
    returns:
        0 if no errors occurred
    '''
    def delete_company_by_name(company_name : str) -> int:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = CompanyTable.__get_delete_company_by_name_query()
        #Run the sql to delete the job
        cursor.execute(query, (company_name,))
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
    
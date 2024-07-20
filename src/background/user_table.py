from collections import OrderedDict
from database_functions import DatabaseFunctions
import json
import uuid
from user import User
from mysql.connector.cursor import MySQLCursor
from mysql.connector.types import RowType, RowItemType
from typing import Dict

class UserTable:
    '''
    get_read_user_by_email_query

    args:
        None
    returns: 
        sql query to read a user by email
    '''
    def __get_read_user_by_email_query() -> str:
        return """
            SELECT *
            FROM USER
            LEFT JOIN UserLocation
            ON User.UserId = UserLocation.UserIdFk
            WHERE Email = %s;
        """
    '''
    get_read_user_by_googleId_query

    args:
        None
    returns:
        sql query to read user by google id
    '''
    def __get_read_user_by_googleId_query() -> str:
        return """
            SELECT *
            FROM USER
            LEFT JOIN UserLocation
            ON User.UserId = UserLocation.UserId
            WHERE Google_Id = %s;
        """
    '''
    get_add_user_query

    args:
        None
    returns:
        sql query to add user
    '''
    def __get_add_user_query() -> str:
        #!IMPORTANT: must be changed if we add a new col
        cols: list[str] = ["UserId", "Email", "Password", "GoogleId", "FirstName", "LastName", "Salt"]
        col_str: str = ", ".join(cols)
        vals: str = ", ".join(["%s"] * len(cols))
        return f"INSERT INTO User ({col_str}) VALUES ({vals})"
    '''
    get_delete_user_by_email_query

    args:
        None
    returns:
        sql query to delete user
    '''
    def __get_delete_user_by_email_query() -> str:
        return f"DELETE FROM User WHERE Email=%s"
    '''
    read_user_by_email

    args:
        email: string email of a user

    returns:
        User with data from sql query
    '''
    def read_user_by_email(email: str) -> User | None:
        cursor: MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query: str = UserTable.__get_read_user_by_email_query()
        cursor.execute(query, (email,))
        result: (Dict[str, RowItemType]) = cursor.fetchone()
        if not result:
            return None
        print("READ USER WITH EMAIL " + email + " GOT "+ str(result))
        return User.create_with_sql_row(result)
    '''
    read_user_by_googleId

    args:
        googleId: the string google id
    returns:
        User object with data from looking up google id in our db
    '''
    def read_user_by_googleId(googleId: str) -> User:
        cursor: MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = UserTable.__get_read_user_by_googleId_query()
        cursor.execute(query, (googleId,))
        result : (Dict[str, RowItemType]) = cursor.fetchone()
        return User.create_with_sql_row(result)
    '''
    add_user

    args:
        user User object to be added
    returns:
        int, 0 if all went well
    '''
    def add_user(user: User) -> int:
        cursor: MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        user_json : Dict = user.to_json()
        query : str = UserTable.__get_add_user_query()
        try:
            #user location points to user not the other way around. Delete the 
            #obj before we add to sql
            user_json["location"]
            del user_json["location"]
        except KeyError:
            pass
        user_json["userId"] = str(user_json["userId"])
        params : list[str] = list(user_json.values())
        print(query)
        print(params)
        cursor.execute(query, params)
        print("USER SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
    '''
    delete_user_by_email

    args:
        email string of the email
    returns:
        int, 0 if all went well
    '''
    def delete_user_by_email(email: str) -> int:
        cursor: MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = UserTable.__get_delete_user_by_email_query()
        cursor.execute(query, (email,))
        print("USER SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
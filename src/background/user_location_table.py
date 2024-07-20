from uuid import UUID
from database_functions import DatabaseFunctions
from location import Location
from typing import Dict
from mysql.connector.cursor import MySQLCursor
from mysql.connector.errors import IntegrityError
from mysql.connector.types import RowType, RowItemType

class UserLocationTable:
    '''
    get_add_location_query

    gets the query to add a UserLocation

    returns:
        query str
    '''
    def __get_add_location_query(location_json : Dict) -> str:
        cols : list[str] = ["userId"]
        cols.extend(list(location_json.keys()))
        col_str : str = ", ".join(cols)
        vals : str = ", ".join(["%s"] * len(cols))
        return f"""
        INSERT INTO UserLocation ({col_str}) VALUES ({vals})
        """
    '''
    get_read_location_query

    gets the query to read a JobLocation by the query str

    returns:
        query str
    '''
    def __get_read_location_query() -> str:
        return f"""
        SELECT * FROM USERLOCATION WHERE UserIdFk = %s
        """
    def __get_delete_location_query() -> str:
        return f"""
        DELETE FROM USERLOCATION WHERE UserIdFk=%s
        """
    '''
    add_user_location

    Adds a users_location to database with a foreign key to User

    args:
        location: Location object that corresponds to user
        user_id: UUID object of the user
    returns:
        0
    '''
    def add_user_location(location: Location, user_id: UUID | str) -> int:
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        print("ADDING USER LOCATION")
        location_json : Dict = location.to_json()
        query = UserLocationTable.__get_add_location_query(location_json)
        #unpack values
        params = [str(user_id), *list(location_json.values())]
        try:
            cursor.execute(query, params)
            DatabaseFunctions.MYDB.commit()
        except IntegrityError:
            cursor.close()
            print("User location already in db")
        print(f"ADDED USER LOCATION")
        cursor.close()
        return 0
    '''
    try_read_location

    attempts to read a users location from the db, returns none if not found

    args:
        user_id: UUID or Str of users id
    returns:
        location object or none
    '''
    def try_read_location(user_id : UUID | str) -> Location | None:
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        print("READING USER LOCATION OBJECT")
        query : str = UserLocationTable.__get_read_location_query()
        cursor.execute(query, (str(user_id),))
        result : (Dict[str, RowItemType]) = cursor.fetchone()
        if not result:
            return None
        return Location.try_get_location_from_sql_row(result)
    '''
    delete_location

    deletes user

    args:
        user_id: UUID or Str of users id
    returns:
        0
    '''
    def delete_location(user_id : UUID | str) -> int:
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        DatabaseFunctions.MYDB.reconnect()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        print("DELETING USER LOCATION OBJECT")
        query : str = UserLocationTable.__get_delete_location_query()
        cursor.execute(query, (str(user_id),))
        return 0
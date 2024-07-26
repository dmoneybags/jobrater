from mysql.connector.types import RowType, RowItemType
from typing import Dict
from location import Location
from uuid import UUID
from typing import Optional
import json


class UserInvalidData(Exception):
        def __init__(self, data: any, message : str ="INVALID DATA PASSED TO CONSTRUCTOR"):
            self.message = message + " DATA RECIEVED: " + str(data)
            super().__init__(self.message)

class User:
    '''
    __init__ main initionalization method for users

    Args:
        UserID: 36 char hex uuid separated by dashes
        email: str email
        password: str password hash
        google_id: str google id if the user auths with google
        fistName: first name string
        lastName: last name strin
        location: Location object for users location
        salt: salt for users password in str format
    
    returns User Object
    '''
    def __init__(self, user_id: UUID, email: str, password: Optional[str], google_id: Optional[str], first_name: str, last_name: str, location: Location, salt: Optional[str]) -> None:
        self.user_id : UUID = user_id
        self.email : str = email
        self.password : str = password
        self.google_id : str = google_id
        self.first_name : str = first_name
        self.last_name : str = last_name
        self.location : Location = location
        self.salt : str = salt
    '''
    create_with_sql_row

    arguments: sql_query_result

    The result of running fetchone, is an itereable that contains dictionaries that contain [column_name, value]

    returns: User object with values from query

    !IMPORTANT: remember to left join location
    '''
    @classmethod
    def create_with_sql_row(cls, sql_query_row: (Dict[str, RowItemType])) -> 'User':
        user_id: UUID
        email: str
        #The nonetypes are due to google users not having password data and non google users not having
        #google_ids
        password: Optional[str] = None
        google_id: Optional[str] = None
        first_name: str
        last_name: str
        location: Location
        salt: Optional[str] = None
        try:
            google_id = sql_query_row["GoogleId"]
            if not google_id:
                #hop out if we don't have a valid google id
                raise KeyError
            print("Loading google user")
            try:
                user_id = UUID(sql_query_row["UserId"])
                email = sql_query_row["Email"]
                first_name = sql_query_row["FirstName"]
                last_name = sql_query_row["LastName"]
                location = Location.try_get_location_from_sql_row(sql_query_row)
                return cls(user_id, email, password, google_id, first_name, last_name, location, salt)
            except KeyError as e:
                raise UserInvalidData(json.dumps(sql_query_row))
        except KeyError as e:
            try:
                print("Loading traditional user")
                print(sql_query_row["UserId"])
                user_id = UUID(sql_query_row["UserId"])
                email = sql_query_row["Email"]
                first_name = sql_query_row["FirstName"]
                last_name = sql_query_row["LastName"]
                location = Location.try_get_location_from_sql_row(sql_query_row)
                password = sql_query_row["Password"]
                salt = sql_query_row["Salt"]
                return cls(user_id, email, password, google_id, first_name, last_name, location, salt)
            except KeyError as e:
                raise UserInvalidData(json.dumps(sql_query_row))
    '''
    create_with_json

    creates a user object with data from a request to add a user

    Args:

    json_object: python dictionary created from json.loads on request query

    returns: User object with data

    !IMPORTANT: because our json_object is created in javascript column names are lowercase first, then camelcase
    '''
    @classmethod
    def create_with_json(cls, json_object : Dict) -> 'User':
        user_id: UUID
        email: str
        #The nonetypes are due to google users not having password data and non google users not having
        #google_ids
        password: Optional[str] = None
        google_id: Optional[str] = None
        first_name: str
        last_name: str
        location: Optional[Location] = None
        salt: Optional[str] = None
        try:
            google_id = json_object["googleId"]
            if not google_id:
                #hop out if we don't have a valid google id
                raise KeyError
            print("Loading google user")
            try:
                #hacky
                try:
                    user_id = UUID(json_object["userId"])
                except ValueError:
                    user_id = ""
                email = json_object["email"]
                first_name = json_object["firstName"]
                last_name = json_object["lastName"]
                if "location" in list(json_object.keys()):
                    location = Location.try_get_location_from_json(json_object["location"])
                return cls(user_id, email, password, google_id, first_name, last_name, location, salt)
            except KeyError as e:
                raise UserInvalidData(json.dumps(json_object))
        except KeyError as e:
            try:
                print("Loading traditional user")
                #hacky
                try:
                    user_id = UUID(json_object["userId"])
                except ValueError:
                    user_id = ""
                email = json_object["email"]
                first_name = json_object["firstName"]
                last_name = json_object["lastName"]
                if "location" in list(json_object.keys()) and json_object["location"] is not None and json_object["location"] != "null":
                    print("Attempting to load location")
                    location = Location.try_get_location_from_json(json_object["location"])
                password = json_object["password"] if "password" in json_object else None
                salt = json_object["salt"] if "salt" in json_object else None
                print("Loaded traditional user")
                return cls(user_id, email, password, google_id, first_name, last_name, location, salt)
            except KeyError as e:
                print("FAILED TO LOAD")
                print(json.dumps(json_object))
                raise UserInvalidData(json.dumps(json_object))
            except Exception as e:
                print("FAILED TO LOAD WITH MISCELLANEOUS EXCEPTION")
                print(e)
                raise e
    '''
    to_json

    returns a dict of the object

    args:
        self: User object
    return:
        dict of users attributes
    '''
    def to_json(self):
        return {
            "userId": str(self.user_id),
            "email": self.email,
            "password": self.password,
            "googleId": self.google_id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "salt": self.salt,
            "location": self.location.to_json() if self.location else None
        }
    
    
        
        
            


    



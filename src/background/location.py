from typing import Dict
from mysql.connector.types import RowType, RowItemType

class LocationInvalidData(Exception):
        def __init__(self, data: any, message : str ="INVALID DATA PASSED TO CONSTRUCTOR"):
            self.message = message + "DATA RECIEVED: " + str(message)
            super().__init__(self.message)

class Location:
    '''
    __init__

    Creates a location object

    MVP version...

    args:

        address str is the street number and street

        ex: 112 Adrian Pl

        city is the city

        ex: Los Gatos

        zip code is the zip code (duh)

        ex: 95032

        state code is 2 letter state code

        ex: CA

        latitude is float latitude

        ex: 70

        longitude is float longitude 

    returns

        location object
    '''
    def __init__(self, address_str: str, city: str, zip_code: str | None, state_code: str | None, latitude: float | None, longitude: float | None) -> None:
        self.address_str = address_str
        self.city = city
        self.zip_code = zip_code
        self.state_code = state_code
        self.latitude = latitude
        self.longitude = longitude
    '''
    try_get_location_from_sql_row

    attempts to get location from sql query result, !IMPORTANT if you do not join location table it will not be able
    to be grabbed

    args:
        sql query row as Dict
    returns Location object or none
    '''
    @classmethod
    def try_get_location_from_sql_row(sql_query_row: (Dict[str, RowItemType])) -> 'Location' | None:
        try:
            sql_query_row["AddressStr"]
        except KeyError:
            return None
        try:
            return cls(sql_query_row["AddressStr"], sql_query_row["City"], sql_query_row["ZipCode"], sql_query_row["StateCode"], sql_query_row["Latitude"], sql_query_row["Longitude"])
        except KeyError:
            raise LocationInvalidData(sql_query_row)
    '''
    try_get_location_from_json

    attmepts to grab location data from json, whether its from user location table or job location table

    args:
        json_object: a dict of values for a userlocation or joblocation
    
    returns Location object if found or none
    '''
    @classmethod
    def try_get_location_from_json(json_object: Dict) -> 'Location' | None:
        try:
            json_object["addressStr"]
        except KeyError:
            return None
        try:
            address_str : str = json_object["addressStr"]
            city : str = json_object["city"]
            zip_code : str | None = json_object["zipCode"] if "zipCode" in list(json_object.keys()) else None
            state_code : str | None = json_object["stateCode"] if "stateCode" in list(json_object.keys()) else None
            latitude : str | None = json_object["latitude"] if "latitude" in list(json_object.keys()) else None
            longitude: str | None = json_object["longitude"] if "longitude" in list(json_object.keys()) else None
            return cls(address_str, city, zip_code, state_code, latitude, longitude)
        except KeyError:
            raise LocationInvalidData(json_object)
    '''
    create_from_google_places_response

    Creates a location object from the json response of our google places query

    Args:
        response_json: example for the input Apple, Cupertino CA

        {'formatted_address': '10600 N Tantau Ave, Cupertino, CA 95014, United States', 'name': 'Apple Apple Park Visitor Center'}
    returns:
        Location object from the json
    '''
    @classmethod
    def create_from_google_places_response(response_json : Dict) -> 'Location':
        location_components : list[str] = response_json["formatted_address"].split(",")
        #split it into its components
        addr_str : str = location_components[0]
        city : str = location_components[1]
        state : str = location_components[2].split(" ")[1]
        zip_code : str = location_components[2].split(" ")[2]
        return cls(addr_str, city, zip_code, state, None, None)
    def to_json(self) -> Dict:
        return {
            "addressStr" : self.address_str,
            "city" : self.city,
            "zipCode" : self.zip_code,
            "stateCode" : self.state_code,
            "latitude" : self.latitude,
            "longitude" : self.longitude 
        }
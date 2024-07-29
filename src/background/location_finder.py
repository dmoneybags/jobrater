from flask import request
import requests
from typing import Dict
import os
from location import Location

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class LocationFinder:
    base_url : str = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    '''
    try_get_company_address

    queries google places to get location of company office, returns none if no match is found

    args:
        company: string company name
        location_str: the string location, usually something like "Cupertino CA"
    returns:
        Location object or none
    '''
    def try_get_company_address(company : str, location_str : str) -> Location | None:
        query : str = f"{company}, {location_str}"
        print("Sending request to read company with query: " +  query)
        google_places_url : str = LocationFinder.base_url + f"?input={query}&inputtype=textquery&fields=name,formatted_address&key={GOOGLE_API_KEY}"

        response : requests.Response = requests.get(google_places_url)
        data : Dict = response.json()
        if 'candidates' in data and data['candidates']:
            return Location.create_from_google_places_response(data['candidates'][0])
        else:
            return None
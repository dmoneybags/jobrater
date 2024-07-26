'''
Execution flow:

Index.js
Listens for: when the popup is openned
Executes: a call to lookup the job location
\/
\/
Google_places.py
Listens for requests on port 5002
'''

from flask import Flask, request, jsonify
import os
import requests
from location_finder import LocationFinder
from typing import Dict
from location_finder import LocationFinder
from location import Location
import os
from helper_functions import HelperFunctions

app : Flask = Flask(__name__)

GOOGLE_API_KEY : str = os.getenv("GOOGLE_API_KEY")
PORT = 5002

'''
try_request_company_address

args:
    request
        company: str, the name of the company
        location_str: str, the text below the company on linkedin
        ex:
        Apple, Cupertino CA
        /\         /\
      Company   Location_str
returns:
    Response with data or 404
'''
@app.route('/location_finder/address', methods=['GET'])
def try_request_company_address():
    print("Sending requests")
    company : str = request.args.get('company')
    location_str : str = request.args.get('locationStr')

    if not company or not location_str:
        return 'Missing required query parameters', 400

    location : Location = LocationFinder.try_get_company_address
    if location:
        return jsonify({'address': location.to_json()})
    else:
        return 'No results found', 404
if __name__ == '__main__':
    HelperFunctions.write_pid_to_temp_file("location_finder")
    app.run(port=PORT)
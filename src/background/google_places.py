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

from flask import request
import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_company_location_object(jobData):
    print("Sending requests")
    company = jobData["company"]
    location_str = jobData["location"]

    if not company or not location_str:
        return 'Missing required query parameters', 400

    query = f"{company}, {location_str}"
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&fields=name,formatted_address&key={GOOGLE_API_KEY}"

    response = requests.get(url)
    data = response.json()
    print(data)
    
    if 'candidates' in data and data['candidates']:
        result = data['candidates'][0]
        return result
    else:
        return 'No results found', 404
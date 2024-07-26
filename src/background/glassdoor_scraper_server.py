'''
Execution flow:

Background.js

Listens for: a tab change event fired when the current tabs url changes
Executes: scrapes the jobId from the url
Sends: a message to the contentScript that we recieved a new job
\/
\/
ContentScript.js
Listens for: the new job event from background.js
Executes the scraping of the linkedin and glassdoor
Calls:
\/
\/
glassdoor_scraper_server
Listens for: requests sent to PORT 5000

TO DO: check that the company isnt somewhere else in our DB
'''
from flask import Flask, jsonify, request
from flask_cors import CORS
import httpx
import json
from glassdoor_scraper import find_companies, scrape_cache, FoundCompany, get_company_data
from random import choice
from auth_server import token_required
from typing import Dict

#Sets up our flask app
app : Flask = Flask(__name__)

PORT : int = 5009

#Allow cross origin requests
CORS(app)

'''
run

runs our glassdoor scraper to get data on the company

Args:
    response
        company: str name of the company
returns:
    json dict of the companies info
'''
@app.route('/get_glassdoor_data', methods=['GET'])
@token_required
async def run():
    #Respond to the preflight options request
    if request.method == 'OPTIONS':
        print("RECIEVED OPTIONS REQUEST, PREFLIGHT")
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    company : str = request.args.get('company', default="NO COMPANY LOADED", type=str)
    #remove non utf8 characters
    company : str = company.encode('utf-8', errors='ignore').decode('utf-8')
    if company == "NO COMPANY LOADED":
        raise AttributeError("Could not load company")
    print("Company Loaded: " + company)
    #gives a list of possible human looking headers, we choose one randomly
    return jsonify(get_company_data(company))
#Runs our server
if __name__ == '__main__':
    app.run(debug=True, port=PORT)
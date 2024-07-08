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
from glassdoor_scraper import find_companies, scrape_cache
from random import choice
from auth_server import token_required

#Sets up our flask app
app = Flask(__name__)
CORS(app)

#Grabs all the relevant glassdoor data for the company given a company as an argument
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
    company = request.args.get('company', default="NO COMPANY LOADED", type=str)
    #remove non utf8 characters
    company = company.encode('utf-8', errors='ignore').decode('utf-8')
    if company == "NO COMPANY LOADED":
        raise AttributeError("Could not load company")
    print("Company Loaded: " + company)
    #gives a list of possible human looking headers, we choose one randomly
    headers_list = [
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.google.com/",
            "DNT": "1"
        },
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/14.1.2 Safari/605.1.15"
            ),
            "Accept-Language": "en-US,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.apple.com/",
            "DNT": "1"
        },
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) "
                "Gecko/20100101 Firefox/89.0"
            ),
            "Accept-Language": "en-US,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.mozilla.org/",
            "DNT": "1"
        },
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/90.0.4430.93 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.google.com/",
            "DNT": "1"
        },
        {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/14.0 Mobile/15E148 Safari/604.1"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.apple.com/",
            "DNT": "1"
        }
    ]
    client = httpx.Client(headers=choice(headers_list), follow_redirects=True)
    #block execution until we find the companies
    companies = await find_companies(company, client)
    #Grab the url to the company
    company_data_url = companies[0]["url_reviews"]
    print("Company Data Url: "+company_data_url)
    #Await scraping the company data from json embeded in the html
    company_data_full = await scrape_cache(company_data_url, client)
    print(json.dumps(company_data_full, indent=2))
    return jsonify({
        "overallRating": company_data_full["ratings"]["overallRating"],
        "businessOutlookRating": company_data_full["ratings"]["businessOutlookRating"],
        "careerOpportunitiesRating": company_data_full["ratings"]["careerOpportunitiesRating"],
        "ceoRating": company_data_full["ratings"]["ceoRating"],
        "compensationAndBenefitsRating": company_data_full["ratings"]["compensationAndBenefitsRating"],
        "cultureAndValuesRating": company_data_full["ratings"]["cultureAndValuesRating"],
        "diversityAndInclusionRating": company_data_full["ratings"]["diversityAndInclusionRating"],
        "seniorManagementRating": company_data_full["ratings"]["seniorManagementRating"],
        "workLifeBalanceRating": company_data_full["ratings"]["workLifeBalanceRating"]
    })
#Runs our server
if __name__ == '__main__':
    app.run(debug=True, port=5009)
#Credit to scrapfly

"""
Python code I copied from scrapfly and editted to run smoother and not use their insanely priced api

ISSUES:

Glassdoor will block our requests sometimes and throw a captcha or however you spell it
"""
import os
from enum import Enum
import asyncio
import json
import os
import re
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, TypedDict
from urllib.parse import urljoin
from flask import Flask, jsonify, request
from loguru import logger as log
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extract_apollo_state(html):
    """Extract apollo graphql state data from HTML source"""
    soup = BeautifulSoup(html, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    if script_tag:
        data = script_tag.string.strip()
        if data:
            # Load JSON data into Python dictionary
            json_data = json.loads(data)
            # Access nested properties
            apollo_cache = json_data["props"]["pageProps"]["apolloCache"]
            return apollo_cache
    try:
        data = re.findall('apolloState":\s*({.+})};', html)[0]
        data = json.loads(data)
        return data
    except IndexError:
        raise ValueError("No apollo state in html: " + html)


def parse_reviews(html) -> Tuple[List[Dict], int]:
    """parse jobs page for job data and total amount of jobs"""
    cache = extract_apollo_state(html)
    xhr_cache = cache["ROOT_QUERY"]
    reviews = next(v for k, v in xhr_cache.items() if k.startswith("employerReviews") and v.get("reviews"))
    return reviews

def parse_salaries(html) -> Tuple[List[Dict], int]:
    """parse jobs page for job data and total amount of jobs"""
    cache = extract_apollo_state(html)
    xhr_cache = cache["ROOT_QUERY"]
    salaries = next(v for k, v in xhr_cache.items() if k.startswith("salariesByEmployer") and v.get("results"))
    return salaries


async def scrape_cache(url: str, session: httpx.AsyncClient):
    """Scrape job listings"""
    first_page_response = session.get(url)  # Await here to fetch the first page asynchronously
    cache = extract_apollo_state(first_page_response.text)
    xhr_cache = cache["ROOT_QUERY"]
    key = [key for key in xhr_cache.keys() if key.startswith("employerReviewsRG")][0]
    company_data = xhr_cache[key]
    return company_data
class Region(Enum):
    """glassdoor.com region codes"""

    UNITED_STATES = "1"
    UNITED_KINGDOM = "2"
    CANADA_ENGLISH = "3"
    INDIA = "4"
    AUSTRALIA = "5"
    FRANCE = "6"
    GERMANY = "7"
    SPAIN = "8"
    BRAZIL = "9"
    NETHERLANDS = "10"
    AUSTRIA = "11"
    MEXICO = "12"
    ARGENTINA = "13"
    BELGIUM_NEDERLANDS = "14"
    BELGIUM_FRENCH = "15"
    SWITZERLAND_GERMAN = "16"
    SWITZERLAND_FRENCH = "17"
    IRELAND = "18"
    CANADA_FRENCH = "19"
    HONG_KONG = "20"
    NEW_ZEALAND = "21"
    SINGAPORE = "22"
    ITALY = "23"

class FoundCompany(TypedDict):
    """type hint for company search result"""
    name: str
    id: str
    url_overview: str
    url_jobs: str
    url_reviews: str
    url_salaries: str
async def find_companies(query: str, session: httpx.AsyncClient) -> List[FoundCompany]:
    """find company Glassdoor ID and name by query. e.g. "ebay" will return "eBay" with ID 7853"""
    result = session.get(
        f"https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={query}"
    )
    print(result.content)
    data = json.loads(result.content)
    companies = []
    for result in data:
        if result["category"] == "company":
            companies.append(
                {
                    "name": result["suggestion"],
                    "id": result["employerId"],
                    "url_overview": Url.overview(result["suggestion"], result["employerId"]),
                    "url_jobs": Url.jobs(result["suggestion"], result["employerId"]),
                    "url_reviews": Url.reviews(result["suggestion"], result["employerId"]),
                    "url_salaries": Url.salaries(result["suggestion"], result["employerId"]),
                }
            )
    return companies
class Url:
    """
    Helper URL generator that generates full URLs for glassdoor.com pages
    from given employer name and ID
    For example:
    > GlassdoorUrl.overview("eBay Motors Group", "4189745")
    https://www.glassdoor.com/Overview/Working-at-eBay-Motors-Group-EI_IE4189745.11,28.htm

    Note that URL formatting is important when it comes to scraping Glassdoor
    as unusual URL formats can lead to scraper blocking.
    """

    @staticmethod
    def overview(employer: str, employer_id: str, region: Optional[Region] = None) -> str:
        employer = employer.replace(" ", "-")
        url = f"https://www.glassdoor.com/Overview/Working-at-{employer}-EI_IE{employer_id}"
        # glassdoor is allowing any prefix for employer name and
        # to indicate the prefix suffix numbers are used like:
        # https://www.glassdoor.com/Overview/Working-at-eBay-Motors-Group-EI_IE4189745.11,28.htm
        # 11,28 is the slice where employer name is
        _start = url.split("/Overview/")[1].find(employer)
        _end = _start + len(employer)
        url += f".{_start},{_end}.htm"
        if region:
            return url + f"?filter.countryId={region.value}"
        return url

    @staticmethod
    def reviews(employer: str, employer_id: str, region: Optional[Region] = None) -> str:
        employer = employer.replace(" ", "-")
        url = f"https://www.glassdoor.com/Reviews/{employer}-Reviews-E{employer_id}.htm?"
        if region:
            return url + f"?filter.countryId={region.value}"
        return url

    @staticmethod
    def salaries(employer: str, employer_id: str, region: Optional[Region] = None) -> str:
        employer = employer.replace(" ", "-")
        url = f"https://www.glassdoor.com/Salary/{employer}-Salaries-E{employer_id}.htm?"
        if region:
            return url + f"?filter.countryId={region.value}"
        return url

    @staticmethod
    def jobs(employer: str, employer_id: str, region: Optional[Region] = None) -> str:
        employer = employer.replace(" ", "-")
        url = f"https://www.glassdoor.com/Jobs/{employer}-Jobs-E{employer_id}.htm?"
        if region:
            return url + f"?filter.countryId={region.value}"
        return url

    @staticmethod
    def change_page(url: str, page: int) -> str:
        """update page number in a glassdoor url"""
        if re.search(r"_P\d+\.htm", url):
            new = re.sub(r"(?:_P\d+)*.htm", f"_P{page}.htm", url)
        else:
            new = re.sub(".htm", f"_P{page}.htm", url)
        assert new != url
        return new
@app.route('/get_glassdoor_data', methods=['GET'])
async def run():
    if request.method == 'OPTIONS':
        print("RECIEVED OPTIONS REQUEST, PREFLIGHT")
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    company = request.args.get('company', default="NO COMPANY LOADED", type=str)
    if company == "NO COMPANY LOADED":
        raise AttributeError("Could not load company")
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    }
    client = httpx.Client(headers=headers)
    companies = await find_companies(company, client)
    company_data_url = companies[0]["url_reviews"]
    print("Company Data Url: "+company_data_url)
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
if __name__ == '__main__':
    app.run(debug=True)
    

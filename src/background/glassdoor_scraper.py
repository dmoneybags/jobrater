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
Listens for: requests sent from content script to scrape glassdoor for a given compnay
Executes the functions from 
\/
\/
glassdoor_scraper
'''

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
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.remote.webdriver import WebDriver, By
from bs4 import BeautifulSoup
import brotli
from html import escape
from typing import Dict, List, Optional, Tuple, TypedDict
from urllib.parse import urljoin
from loguru import logger as log
from random import choice

def get_random_header():
    headers_list : list[Dict] = [
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
    return choice(headers_list)

def get_driver(headless: bool = True):
    # Set up the proxy
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = "127.0.0.1:8888"
    proxy.ssl_proxy = "127.0.0.1:8888"
    # Set up the headers
    header: Dict = get_random_header()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("intl.accept_languages", "en-US,en;q=0.9")
    profile.set_preference('general.useragent.override', header["User-Agent"])
    profile.set_preference("intl.accept_languages", header["Accept-Language"])
    profile.set_preference("network.http.accept-encoding", header["Accept-Encoding"])
    profile.set_preference("network.http.upgrade-insecure-requests", "1")
    profile.set_preference("privacy.donottrackheader.enabled", True)
    # Configure Firefox options
    firefox_options = Options()
    #firefox_options.proxy = proxy
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference('useAutomationExtension', False)
    firefox_options.set_preference("media.peerconnection.enabled", False)

    # Optional: disable notifications and popups
    firefox_options.set_preference("dom.webnotifications.enabled", False)
    firefox_options.set_preference("dom.push.enabled", False)
    if headless:
        firefox_options.add_argument("--headless")
    #firefox_options.proxy = proxy

    # Initialize the WebDriver with the options
    driver: WebDriver = webdriver.Firefox(options=firefox_options, firefox_profile=profile)
    driver.set_window_size(2560, 1440)
    return driver

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
async def scrape_cache(url: str, session: WebDriver):
    """Scrape job listings"""
    session.get(url)
    first_page_response = session.page_source  # Await here to fetch the first page asynchronously
    cache = extract_apollo_state(first_page_response)
    xhr_cache = cache["ROOT_QUERY"]
    key = [key for key in xhr_cache.keys() if key.startswith("employerReviewsRG")][0]
    company_data = xhr_cache[key]
    return company_data
async def get_company_data(company: str) -> Dict:
    with get_driver() as client:
        #block execution until we find the companies
        companies : list[FoundCompany] = await find_companies(company, client)
        #Grab the url to the company
        company_data_url : str = companies[0]["url_reviews"]
        print("Company Data Url: "+company_data_url)
        #Await scraping the company data from json embeded in the html
        company_data_full : Dict = await scrape_cache(company_data_url, client)
    print(json.dumps(company_data_full, indent=2))
    return {
        "overallRating": company_data_full["ratings"]["overallRating"],
        "businessOutlookRating": company_data_full["ratings"]["businessOutlookRating"],
        "careerOpportunitiesRating": company_data_full["ratings"]["careerOpportunitiesRating"],
        "ceoRating": company_data_full["ratings"]["ceoRating"],
        "compensationAndBenefitsRating": company_data_full["ratings"]["compensationAndBenefitsRating"],
        "cultureAndValuesRating": company_data_full["ratings"]["cultureAndValuesRating"],
        "diversityAndInclusionRating": company_data_full["ratings"]["diversityAndInclusionRating"],
        "seniorManagementRating": company_data_full["ratings"]["seniorManagementRating"],
        "workLifeBalanceRating": company_data_full["ratings"]["workLifeBalanceRating"]
    }
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
async def find_companies(query: str, session: WebDriver) -> List[FoundCompany]:
    """find company Glassdoor ID and name by query. e.g. "ebay" will return "eBay" with ID 7853"""
    print("URL: " + f"https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={query}")
    # Set a realistic timeout
    # UPDATE, now set upstream
    url = f"https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={query}"
    print("URL: "+ url)
    session.get(url)
    result: str = session.find_element(By.XPATH, "/html/body").text
    try:
        data = json.loads(result)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("DATA CONVERSION FAILED FOR: " + result)
        while(1):
            pass
        raise e
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

    

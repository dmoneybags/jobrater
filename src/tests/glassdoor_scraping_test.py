import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'background')))
from glassdoor_scraper import get_company_data, get_driver
from random import choice
import asyncio
import time

class GlassdoorScrapingTests:
    print("Checking glassdoor scraping success rate")
    companies: list[str] = ["Apple", "Google", "ADP", "BlackRock", "Deloitte",
                            "Verizon", "Coherent", "T-mobile", "Nvidia", "Edison",
                            "Microsoft", "Amazon", "Cisco", "Yamaha", "Mercedes"]
    async def checkSuccessRate(numAttempts: int = 200) -> float:
        errors: int = 0
        for i in range(numAttempts):
            company: str = choice(GlassdoorScrapingTests.companies)
            try:
                await get_company_data(company)
            except ValueError as e:
                print(f"Failed on {company} with error of {e}")
                errors += 1
            except IndexError as e:
                print(f"Failed on {company} to grab jobs with error of {e}")
                errors += 1
            time.sleep(1)
        print(f"Got success rate of {1 - errors/numAttempts}")
        return 1 - errors/numAttempts

if __name__ == "__main__":
    asyncio.run(GlassdoorScrapingTests.checkSuccessRate())
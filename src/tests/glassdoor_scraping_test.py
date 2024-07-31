import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'background')))
from glassdoor_scraper import get_company_data
from random import choice
import asyncio

class GlassdoorScrapingTests:
    print("Checking glassdoor scraping success rate")
    companies: list[str] = ["Apple", "Google", "ADP", "BlackRock", "Deloitte",
                            "Verizon", "AT&T", "T mobile", "Sprint", "Macys", "Edison",
                            "Microsoft", "Amazon", "Cisco", "Yamaha", "Mercedes"]
    async def checkSuccessRate(numAttempts: int = 20) -> float:
        errors: int = 0
        for i in range(numAttempts):
            company: str = choice(GlassdoorScrapingTests.companies)
            try:
                await get_company_data(company)
            except Exception as e:
                print(f"Recieved error for {company}")
                print(e)
                errors += 1
        print(f"Got success rate of {1 - errors/numAttempts}")
        return 1 - errors/numAttempts

if __name__ == "__main__":
    asyncio.run(GlassdoorScrapingTests.checkSuccessRate())
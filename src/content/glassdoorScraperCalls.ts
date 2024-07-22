/*
Execution flow

ContentScipt
scrapes job info, checks if the companies data is in the db
IF NOT
\/
\/
glassdoorScrapercalls
calls our python flask server to dispatch the glassdoor scraper
*/

import { Company, CompanyFactory } from "./company"
import { GlassdoorScraperError } from "./errors"
import { DatabaseCalls } from "./databaseCalls";

const GLASSDOORSERVER = "http://localhost:5009";

class GlassdoorScraping {
    /**
     * scrapeCompanyInfoIfNeeded
     * 
     * Checks if the company is in the db and if not calls our glassdoor scraper to scrape it.
     * if for any reason the glassdoor scraper errors (oh and yes it will) it will leak the error
     * 
     * @param {string} companyName - the name we are scraping for
     * @returns {Promise<Company | null | void>}- a promise that is: the company, null (already in db), void (Error)
     */
    static scrapeCompanyInfoIfNeeded = (companyName: string):Promise<Company | null | void> => {
        return DatabaseCalls.checkIfCompanyExists(companyName)
            .then((doesExist: boolean):Promise<Company | null> => {
                return new Promise((resolve, reject) => {
                    if (doesExist) {
                        console.log("Returning job data without scraping for company");
                        resolve(null);
                    } else {
                        console.log("SCRAPING GLASSDOOR");
                        GlassdoorScraping.scrapeGlassdoorInfo(companyName)
                            .then(companyData => {
                                const company: Company = CompanyFactory.generateFromJson(companyData);
                                resolve(company);
                            })
                            //THIS IS AN ERROR FROM OUR GLASSDOOR SERVER
                            .catch(error => {
                                reject(new GlassdoorScraperError("Failed to scrape glassdoor with error " + error));
                            });
                    }
                })
            })
            //THIS IS AN ERROR FROM OUR DATABASE SERVER
            //TODO: How to handle?
            .catch(error => {
                //Log that the company check data couldn't be grabbed
                console.error("-------- COULDNT COMPLETE COMPANY INFO --------");
            });
    }
    /**
     * scrapeGlassdoorInfo
     * 
     * calls our glassdoor scraper to get company data
     * 
     * @param {string} companyName - name of the company we are scraping for
     * @returns {Promise<Record<string, any>>} the promise returning the json
     */
    static scrapeGlassdoorInfo = (companyName: string):Promise<Record<string, any>> => {
        //create a promise to resolve it asynchronously
        console.log("Sending request for glassdoor data")
        return new Promise((resolve, reject) => {
            //Our python program runs on port 5009 on our local server
            var xhr: XMLHttpRequest = new XMLHttpRequest();
            //call an http request
            xhr.open('GET', GLASSDOORSERVER + '/get_glassdoor_data?company=' + encodeURIComponent(companyName), true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status === 200) {
                    //change it to json
                    var responseJson: Record<string, any> = JSON.parse(xhr.responseText);
                    console.log(responseJson)
                    //resolve the promist
                    resolve(responseJson);
                } else {
                    //Didnt get a sucessful message
                    reject(new Error(`Request failed with status ${xhr.status}`));
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(new Error(`Request failed with status ${xhr.statusText}`));
            };
            //send our response
            xhr.send();
        });
    };
}
import { ScrapingError } from "./errors"
import { HelperFunctions } from "./helperFunctions";
import { Job, JobFactory } from "./job"

export class LinkedInScrapingFunctions {
    /**
     * getJobInfoData
     * 
     * scrapes the little job info container below the job title and returns json containing
     * 
     * @returns {Record<string, any>}: {paymentFreq: string, paymentBase: number, }
     */
    static getJobInfoData = (): Record<string, any> => {
        const json = {
            "paymentFreq": "",
            "paymentBase": 0,
            "paymentHigh": 0,
            "mode": "",
            "careerStage": ""
        };
        //holds salary, on site hybrid remote, 
        let infoBox: Element = document.getElementsByClassName("job-details-jobs-unified-top-card__job-insight")[0];
        if (!infoBox || !infoBox.textContent) {
            infoBox = document.getElementsByClassName("mt2 mb2")[0];
            if (!infoBox) {
                console.warn("info_box_text not found");
                return json;
            }
        }
        const infoBoxText: string = (infoBox.textContent ?? "").trim();
        const infoBoxContents: string[] = infoBoxText.split("\n");
        const modes: string[] = ["Remote", "Hybrid", "On-site"];
        const careerStages: string[] = ["Associate", "Entry level", "Mid-Senior level", "Executive", "Director", ]
        for (let element of infoBoxContents){
            //cut out any conversion errors
            let str: String = String(element);
            //check each mode to see if defining text existings
            for (let mode of modes){
                //Check if the string includes the text of our modes
                if (str.includes(mode)){
                    //mode is the string of hybrid onsite or remote
                    json["mode"] = mode;
                    continue;
                }
            };
            //Same for careerStages
            for (let careerStage of careerStages){
                if (str.includes(careerStage)){
                    json["careerStage"] = careerStage;
                    console.log("found careerStage of " + careerStage); 
                    continue;
                }
            };
            //Check for our salary element
            if (str.includes("$")){
                if (str.includes("yr")){
                    json["paymentFreq"]  = "yr";
                }
                if (str.includes("hr")){
                    json["paymentFreq"]  = "hr";
                }
                //Find our 2 numbers in the string by matching a regular expression
                const regex = /[\d,]+\.?\d*/g;
                const matches = str.match(regex);
                
                if (matches) {
                    // Convert matched strings to numbers and return as an array
                    const amounts: number[] = matches.map(match => parseFloat(match.replace(/,/g, '')));
                    json["paymentBase"] = amounts[0];
                    if (amounts.length < 2){
                        continue;
                    }
                    json["paymentHigh"] = amounts[1];
                }
            }
        };
        return json;
    };
    /**
     * getCompany
     * 
     * scrapes the company name from the linkedIn job posting
     * 
     * @returns {string} company
     */
    static getCompany = ():string => {
        //use document methods here to grab the info we need
        //companyNameBox holds the company name, located at the very top of the posting
        const companyNameBox: Element = document.getElementsByClassName("job-details-jobs-unified-top-card__company-name")[0];
        let company: string = "";
        let job: string = "";
        //Check if it exists
        if (companyNameBox) {
            company = (companyNameBox.textContent ?? "").trim();
            if (company === ""){
                throw new ScrapingError("Company name box not found");
            }
            console.log("Company: " + company);
            return company;
        }
        throw new ScrapingError("Company name box not found");
    }
    /**
     * getJob
     * 
     * scrapes the job name from the linkedIn job posting
     * 
     * @returns {string} job
     */
    static getJob = ():string => {
        //holds the job posting below the company name
        const jobNameBox: Element = document.getElementsByClassName("job-details-jobs-unified-top-card__job-title")[0];
        //Check if it exists
        if (jobNameBox) {
            const job = (jobNameBox.textContent ?? "").trim();
            if (job === ""){
                throw new ScrapingError("Job is empty");
            }
            console.log("Job: " + job);
            return job;
        } 
        throw new ScrapingError("Could not find job box");
    }
    /**
     * getCompanyAndJob
     * 
     * gets the company and job name from the posting
     * @returns {string[]} [companyName, jobName]
     */
    static getCompanyAndJob = ():string[] => {
        const company: string = LinkedInScrapingFunctions.getCompany();
        const job: string = LinkedInScrapingFunctions.getJob();
        return [company, job];
    }
    /**
     * getJobDescription
     * 
     * scrapes the page for the job description
     * 
     * @returns {string} job description
     */
    static getJobDescription = ():string | null => {
        const jobDescriptionElem: Element = document.getElementsByClassName("jobs-description")[0]
        if (!jobDescriptionElem){
            return null
        }
        return jobDescriptionElem.textContent!.trim()
    }
    /**
     * getTopBoxData
     * 
     * "Top box" data contains how long the job was posted ago, the locationstr, and the num applicants
     * 
     * @returns {Record<string, any>} {location: string, secondsPostedAgo: number, applicants: number}
     */
    static getTopBoxData = ():Record<string, any> => {
        let topBox: Element = document.getElementsByClassName("job-details-jobs-unified-top-card__primary-description-container")[0];
        if (!topBox) {
            console.warn("top_box_text not found");
            throw new ScrapingError("Could not find top box");
        }
        //get the string data
        let topBoxText: string = (topBox.textContent ?? "").trim();
        if (topBoxText === ""){
            throw new ScrapingError("top box text is empty");
        }
        console.log("Top Box Text: " + topBoxText)
        //remove empty strings
        topBoxText = topBoxText.replace(/[\r\n]+/g, '');
        //split by the dots
        if (topBoxText.includes("·")){
            var topBoxContents: string[] = topBoxText.split("·");
        } else {
            topBoxContents = topBoxText.split("\n");
        }
        const topBoxData: Record<string, any> = {
            "location": "",
            "secondsPostedAgo": 0,
            "applicants": 0
        };
        //will always show location first
        topBoxData["location"] = topBoxContents[0];
        //time posted ago second
        let timeStr: string = topBoxContents[1];
        console.log("TimeStr: " + timeStr);
        //If the job was reposted remove the prefix
        const prefix: string = "Reposted ";
        if (timeStr.includes(prefix)){
            timeStr = timeStr.substring(prefix.length);
        }
        //When we split into words we get weird empty strings
        let timeComponents: string[] = timeStr.split(" ").filter(element => element !== "");
        //How many of a certain timeframe do we have
        const numberOfTimeframe: number = Number(timeComponents[0]);
        //hours, days, weeks, months
        const timeFrame: string = timeComponents[1];
        console.log("Timeframe: " + timeFrame)
        topBoxData["secondsPostedAgo"] = numberOfTimeframe * HelperFunctions.getTimeFrameSeconds(timeFrame);
        //Applicants 3rd
        const applicantStr: string = topBoxContents[2];
        //again splitting gets us weird empty strings
        //numbers var thats a list of str... haha...
        let numbers: string[] = applicantStr.split(" ").filter(element => element !== "");
        //Lets find the numbers in the components
        numbers = numbers.filter(str => !isNaN(Number(str)));
        topBoxData["applicants"] = Number(numbers[0]);
        return topBoxData;
    }
    /**
     * scrapeJobInfo
     * 
     * Main scraping function for linkedin job, scapes the page and creates the json for all the job data we need
     * 
     * @returns {Record<string, any>} jobData
     */
    static scrapeJobInfo = (): Record<string, any> => {
        //jobData is the main dict, we start with it and compile the other subDicts into it
        let jobData: Record<string, any> = {
            "company": "",
            "job": ""
        };
        let [company, job]: string[] = LinkedInScrapingFunctions.getCompanyAndJob();
        //Load the info it
        jobData["company"]["companyName"] = company;
        jobData["job"] = job;
        let description = LinkedInScrapingFunctions.getJobDescription();
        jobData["description"] = description;
        //Top box shows location, days posted ago, and applicants
        const topBoxData = LinkedInScrapingFunctions.getTopBoxData();
        const descriptionData = LinkedInScrapingFunctions.getJobInfoData();
        return { ...jobData, ...topBoxData, ...descriptionData };
    }
    //Called every single time a new job is loaded. Grabs information on the job and sets it in the DB. 
    //View will then render the db.
    static LinkedInJobLoaded = (jobId, attempts: number = 3): Promise<Job> => {
        return new Promise((resolve, reject) => {
            HelperFunctions.waitForDocumentLoaded()
                .then(() => {
                    console.log("New Job Loaded");
                    //Grabs the data directly from the linkedin website
                    var jobDataJson: Record<string, any> = {};
                    try{
                        jobDataJson = HelperFunctions.tryWithRetry(LinkedInScrapingFunctions.scrapeJobInfo, attempts);
                    } catch (error){
                        if (error instanceof ScrapingError){
                            console.error("Failed to scrape linkedin after 3 retries");
                            reject(error)
                        } 
                        throw error;
                    }
                    //Store the job ID as a UUID for our db
                    jobDataJson["jobId"] = jobId;
                    const job: Job = JobFactory.generateFromJson(jobDataJson);
                    resolve(job);
                });
        })
    }
}
/*
scrapeCompanyInfoIfNeeded(jobDataJson)
    .then((jobDataJson) => {
        sendMessageToAddJob(jobDataJson)
    })
*/
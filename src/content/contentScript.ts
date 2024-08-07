/*
Execution

background.js
Listens for: tab changes with the required linkedin urls 
Executes: processing the query to get the job id 
Sends: a message to contentscript to scrape the job
\/
\/
contentScript.js
Listens for: requests with the type NEW
Executes: scraping for linkedin and glassdoor
Sends: a message for db to handle the job
*/


//Runs all the content after we get new jobloaded message, basically grabbing all our data and putting it in our db
//ISSUES:
//topbox has trouble being grabbed when the page first loads in
//TO DO:
//CRUD Methods X
//Will do later: Add competitiveness algo taking, applicants, company and job prestige, required experience
//Get company address X
//Google maps api
//User data
//UI
//Payments
//deployment
//question: what to do on addJob with no token?
import { LinkedInScrapingFunctions } from "./linkedinScrapingFunctions";
import { Job, JobFactory } from "./job"
import { DatabaseCalls } from "./databaseCalls";
import { LocalStorageHelper } from "./localStorageHelper";

//MAIN
(() => {
    const handleJobPromise = (promise:Promise<Job>) => {
        promise.then((jobread:Job):void => {
            DatabaseCalls.sendMessageToAddJob(jobread)
            .then((responseJson: Record<string, any>) => {
                const completeJob: Job = JobFactory.generateFromJson(responseJson);
                LocalStorageHelper.addJob(completeJob);
                let message : Record<string, any> = {type: 'NEW_JOB', payload: completeJob };
                window.postMessage(message, '*');
            })
        })
    }
    //No job is loaded yet
    let currentJob: string = "";
    //Listener that activates every time a new job message is sent from background
    //seeing a new url that corresponds to a job url
    chrome.runtime.onMessage.addListener((obj, sender, response) => {
        console.log("Message recieved");
        //Only arg to the message is the job id
        const { type, company, jobId } = obj;
        currentJob = jobId;
        console.log("job Id loaded" + jobId);
        if (type === "NEW" ) {
            switch (company){
                case "LINKEDIN":
                    handleJobPromise(LinkedInScrapingFunctions.LinkedInJobLoaded(jobId));
            }
            
        }
    });
})();
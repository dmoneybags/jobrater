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
TEST = true;
(() => {
    //No job is loaded yet
    let currentJob = "";
    //Listener that activates every time a new linkedin job is selected
    chrome.runtime.onMessage.addListener((obj, sender, response) => {
        console.log("Message recieved");
        //Only arg to the message is the job id
        const { type, value, jobId } = obj;
        if (type === "NEW") {
            currentJob = jobId;
            console.log(jobId);
            newJobLoaded(jobId);
        }
    });

    // Common stopwords to exclude
    const stopwords = [
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", 
        "into", "is", "it", "of", "on", "or", "that", "the", "to", "with", "will",
        "firm", "about", "our", "their", "team", "role", "process", "through",
        "day", "regional", "well", "can", "please", "including", "individual", "work",
        "benefits", "we", "job", "company", "select", "review", "stakeholders", "plan",
        "services", "products", "qualifications", "what", "you", "other", "your", "because",
        "need", "don", "t", "have", "s", "who", "looking", "great", "also", "want", "good", "all",
        "from", "all", "over", "candidates", "feel", "they", "meet", "apply", "note", "criteria", "note",
        "re", "like", "this", "us", "ll", "ve"
    ];
    // Function to extract keywords
    const extractKeywords = () => {
        const jobDescriptionBox = document.getElementById("job-details");

        const text = jobDescriptionBox.textContent.trim();
        // Convert the text to lower case and split it into words
        const words = text.toLowerCase().match(/\b\w+\b/g);

        // Filter out stopwords
        const keywords = words.filter(word => !stopwords.includes(word));

        // Count the frequency of each keyword
        const keywordFrequency = {};
        keywords.forEach(word => {
            keywordFrequency[word] = (keywordFrequency[word] || 0) + 1;
        });

        // Sort keywords by frequency (most frequent first)
        const sortedKeywords = Object.keys(keywordFrequency).sort((a, b) => keywordFrequency[b] - keywordFrequency[a]);

        return sortedKeywords;
    };
    const getTimeFrameSeconds = (timeFrame) => {
        let seconds = 0;
        switch (timeFrame) {
            case 'months':
                seconds = 7 * 24 * 3600;
                break;
            case 'month':
                seconds = 7 * 24 * 3600;
                break;
            case 'weeks':
                seconds = 7 * 24 * 3600;
                break;
            case 'week':
                seconds = 7 * 24 * 3600;
                break;
            case 'days':
                seconds = 24 * 3600;
                break;
            case 'day':
                seconds = 24 * 3600;
                break;
            case 'hours':
                seconds = 3600;
                break;
            case 'hour':
                seconds = 3600;
                break;
            case 'minutes':
                seconds = 60;
                break;
            case 'minute':
                seconds = 60;
                break;
            default:
                console.error('Unsupported timeframe');
                break;
        }
        return seconds;
    }
    //Top box is the box below the job name that shows the location, time posted and applicants
    const getTopBoxData = () => {
        let topBox = document.getElementsByClassName("job-details-jobs-unified-top-card__primary-description-container")[0];
        if (!topBox) {
            console.warning("top_box_text not found");
        }
        //get the string data
        let topBoxText = topBox.innerText;
        console.log("Top Box Text: " + topBoxText)
        //remove empty strings
        topBoxText = topBoxText.replace(/[\r\n]+/g, '');
        //split by the dots
        if (topBoxText.includes("·")){
            var topBoxContents = topBoxText.split("·");
        } else {
            topBoxContents = topBoxText.split("\n");
        }
        const topBoxData = {
            "location": "",
            "secondsPostedAgo": 0,
            "applicants": 0
        };
        //will always show location first
        topBoxData["location"] = topBoxContents[0];
        //time posted ago second
        let timeStr = topBoxContents[1]
        console.log("TimeStr: " + timeStr);
        //If the job was reposted remove the prefix
        const prefix = "Reposted ";
        if (timeStr.includes(prefix)){
            timeStr = timeStr.substring(prefix.length);
        }
        //When we split into words we get weird empty strings
        let timeComponents = timeStr.split(" ").filter(element => element !== "");
        //How many of a certain timeframe do we have
        const numberOfTimeframe = timeComponents[0];
        //hours, days, weeks, months
        const timeFrame = timeComponents[1];
        console.log("Timeframe: " + timeFrame)
        topBoxData["secondsPostedAgo"] = numberOfTimeframe * getTimeFrameSeconds(timeFrame);
        //Applicants 3rd
        const applicantStr = topBoxContents[2];
        //again splitting gets us weird empty strings
        let numbers = applicantStr.split(" ").filter(element => element !== "");
        //Lets find the numbers in the components
        numbers = numbers.filter(str => !isNaN(str));
        topBoxData["applicants"] = numbers[0];
        return topBoxData;
    }
    const getJobInfoData = () => {
        //holds salary, on site hybrid remote, 
        let infoBox = document.getElementsByClassName("job-details-jobs-unified-top-card__job-insight")[0];
        if (!infoBox) {
            infoBox = document.getElementsByClassName("mt2 mb2")[0];
            if (!infoBox) {
                console.warn("info_box_text not found");
            }
        }
        const infoBoxText = infoBox.textContent.trim();
        const infoBoxContents = infoBoxText.split("\n");
        
        const json = {
            "paymentFreq": "",
            "paymentBase": "",
            "paymentHigh": "",
            "mode": "",
            "careerStage": ""
        };

        const modes = ["Remote", "Hybrid", "On-site"];
        const careerStages = ["Associate", "Entry level", "Mid-Senior level", "Executive", "Director", ]
        for (let element of infoBoxContents){
            //cut out any conversion errors
            let str = String(element);
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
                     amounts = matches.map(match => parseFloat(match.replace(/,/g, '')));
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

    const getCompanyAndJob = () => {
        //use document methods here to grab the info we need
        //companyNameBox holds the company name, located at the very top of the posting
        const companyNameBox = document.getElementsByClassName("job-details-jobs-unified-top-card__company-name")[0];
        let company = "";
        let job = "";
        //Check if it exists
        if (companyNameBox) {
            company = companyNameBox.textContent.trim();
            console.log("Company: " + company);
        } else {
            //couldn't find company box
            console.error("Company name box not found");
        }
        //holds the job posting below the company name
        const jobNameBox = document.getElementsByClassName("job-details-jobs-unified-top-card__job-title")[0];
        //Check if it exists
        if (jobNameBox) {
            job = jobNameBox.textContent.trim();
            console.log("Job: " + job);
        } else {
            //Couldnt find the job name
            console.warning("Job name box not found");
        }
        return [company, job];
    }

    const scrapeJobInfo = () => {
        //jobData is the main dict, we start with it and compile the other subDicts into it
        let jobData = {
            "company": "",
            "job": "",
            "keywords": ""
        };
        let [company, job] = getCompanyAndJob();
        // Extract keywords from the job description
        const keywords = extractKeywords();
        //Load the info it
        jobData["company"] = company;
        jobData["job"] = job;
        jobData["keywords"] = keywords;
        //Top box shows location, days posted ago, and applicants
        const topBoxData = getTopBoxData();
        const descriptionData = getJobInfoData();
        return { ...jobData, ...topBoxData, ...descriptionData };
    }
    //Calls our python program to scrape info from glassdoor
    const scrapeGlassdoorInfo = (company) => {
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our python program runs on port 5000 on our local server
            var xhr = new XMLHttpRequest();
            //call an http request
            xhr.open('GET', 'http://localhost:5000/get_glassdoor_data?company=' + encodeURIComponent(company), true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status === 200) {
                    //change it to json
                    var response = JSON.parse(xhr.responseText);
                    console.log(response)
                    //resolve the promist
                    resolve(response);
                } else {
                    //Didnt get a sucessful message
                    console.error('Request failed. Status:', xhr.status);
                    reject(xhr.status);
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(xhr.statusText);
            };
            //send our response
            xhr.send();
        });
    };
    //This function simply checks if the company exists by 
    //querying our db
    const checkIfCompanyExists = (company) => {
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our python program runs on port 5000 on our local server
            var xhr = new XMLHttpRequest();
            //call an http request
            console.log("Sending Request to get company");
            xhr.open('GET', 'http://localhost:5001/databases/read_company?company=' + encodeURIComponent(company), true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status == 200){
                    console.log("Recieved the company from the db");
                    resolve(true)
                } else {
                    console.log("Couldn't find the company in our database, scraping glassdoor");
                    resolve(false)
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(xhr.statusText);
            };
            //send our response
            xhr.send();
        });
    }
    const scrapeCompanyInfoIfNeeded = (jobDataJson) => {
        return checkIfCompanyExists(jobDataJson["company"])
        .then((doesExist) => {
            return new Promise((resolve, reject) => {
                if (doesExist) {
                    console.log("Returning job data without scraping for company");
                    resolve(jobDataJson);
                } else {
                    console.log("SCRAPING GLASSDOOR");
                    scrapeGlassdoorInfo(jobDataJson["company"])
                        .then(processedValue => {
                            //merge our dictionaries
                            jobDataJson = { ...jobDataJson, ...processedValue };
                            resolve(jobDataJson);
                        })
                        //THIS IS AN ERROR FROM OUR GLASSDOOR SERVER
                        .catch(error => {
                            //Log that the glassdoor data couldn't be grabbed
                            console.error("-------- GLASS DOOR SCRAPE FAILED --------");
                            resolve(jobDataJson);
                        });
                }
            })
        })
        //THIS IS AN ERROR FROM OUR DATABASE SERVER
        .catch(error => {
            //Log that the company check data couldn't be grabbed
            console.error("-------- COULDNT COMPLETE COMPANY INFO --------");
        });
    }
    const waitForDocumentLoaded = () => {
        return new Promise((resolve) => {
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                resolve();
            } else {
                document.addEventListener('DOMContentLoaded', resolve);
            }
        });
    }
    const sendMessageToAddJob = (jobDataJson) => {
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our database program runs on port 5001 on our local server
            var xhr = new XMLHttpRequest();
            //call an http request
            xhr.open('POST', 'http://localhost:5001/databases/add_job?jobJson=' + encodeURIComponent(JSON.stringify(jobDataJson)), true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status === 200) {
                    //change it to json
                    var response = xhr.responseText;
                    console.log("Add Job Request Suceeded");
                } else {
                    //Didnt get a sucessful message
                    console.error('Request failed. Status:', xhr.status);
                    reject(xhr.status);
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(xhr.statusText);
            };
            //send our response
            xhr.send();
        });
    };
    //Called every single time a new job is loaded. Grabs information on the job and sets it in the DB. 
    //View will then render the db.
    const newJobLoaded = (jobId) => {
        waitForDocumentLoaded().then(() => {
            console.log("New Job Loaded");
            //Grabs the data directly from the linkedin website
            var jobDataJson = scrapeJobInfo();
            //Store the job ID as a UUID for our db
            jobDataJson["jobId"] = jobId;
            //Grabs the info from our python program which scrapes the glassdoor website.
            scrapeCompanyInfoIfNeeded(jobDataJson)
            .then((jobDataJson) => {
                sendMessageToAddJob(jobDataJson)
            })
        });
    }
    newJobLoaded();
})();

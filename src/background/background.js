/*
First order data needed:

*from url
Job UUID
*Scraping
Job Title
Company
salary range
remote/hybrid/in person

Second order data needed:

Glassdoor data
Job site location
company financials
company overview

Tertiary data needed:

commute time
*/
// Listen for tab updates to specific LinkedIn job URLs
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    //Check for URL matches
    if (tab.url && (tab.url.includes("linkedin.com/jobs/search") || 
    tab.url.includes("linkedin.com/jobs/collections/recommended/") || 
    tab.url.includes("linkedin.com/jobs/view/"))) {
        if (changeInfo.status === 'complete') {
            //Process the url str to get the jobId
            const queryParameters = tab.url.split("?")[1];
            const urlParameters = new URLSearchParams(queryParameters);
            console.log('URL Parameters:', urlParameters);
            //Send a message to contentScript to scrape pages and enter it in our db
            chrome.tabs.sendMessage(tabId, {
                type: "NEW",
                jobId: urlParameters.get("currentJobId")
            });
        }
    }
});
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    //CREATE
    if (request.greeting === "ADD_JOB") {
        console.log("Received job data:", request.jobDataJson);
        JobDatabases.addNewJob(request.jobDataJson);
        sendResponse({ farewell: "Job added successfully" });
    }
    //READ
    if (request.greeting === "GET_MOST_RECENT_JOB") {
        console.log("Recieved get most recent job message")
        JobDatabases.readMostRecentJob()
        .then((jobJson) => {
            sendResponse({response: jobJson, farewell: "Job read successfully" });
        });
    }
    //UPDATE
    if (request.greeting === "UPDATE_JOB") {
        console.log("Recieved update job notification for " + mostRecentJob["job"] + " at " + mostRecentJob["company"]);
        JobDatabases.updateJobById(request.jobDataJson);
        sendResponse({ farewell: "Job update successfully" });
    }
    //DELETE
    if (request.greeting === "DELETE_JOB") {
        console.log("Recieved update job notification for " + mostRecentJob["job"] + " at " + mostRecentJob["company"]);
        JobDatabases.deleteJobById(request.jobId);
        sendResponse({ farewell: "Job delete successfully" });
    }   
});

// current schema:

// applicants
// "0"
// businessOutlookRating
// 0.55
// careerOpportunitiesRating
// 3.6
// careerStage
// "Entry level"
// ceoRating
// 0.45
// company
// "Precision Castparts"
// compensationAndBenefitsRating
// 3.7
// cultureAndValuesRating
// 2.7
// diversityAndInclusionRating
// 3.2
// job
// "Inside Sales Representative Level 3"
// jobId
// "3945501713"
// keywords
// (552) ['customer', 'customers', 'sales', 'u', 'employees', 'required', 'employee', 'applications', 'inside', 'pricing', 'data', 'information', 'business', 'regulations', 'operations', 'highly', 'assigned', 'maintain', 'essential', 'functions', 'vision', 'manufacturing', 'castings', 'critical', 'quality', 'e', 'responsibilities', 'leads', 'resolve', 'excellent', 'account', 'ensuring', 'service', 'duties', 'manager', 'product', 'up', 'database', 'orders', 'related', 'shipping', 'based', 'dates', 'ensure', 'shop', 'access', 'experience', 'environment', 'preferred', 'must', 'perform', 'occasionally', 'eligible', 'bonus', 'paid', 'receive', 'export', '10', 'precision', 'castparts', 'corp', 'market', 'structural', 'airfoil', 'aerostructures', 'aerospace', 'addition', 'producer', 'gas', 'materials', 'such', 'not', 'make', 'its', 'high', 'cost', 'time', 'delivering', 'value', 'while', 'strategic', 'growth', 'irvine', 'systems', 'engine', 'assembly', 'include', 'cnc', 'position', 'managing', 'key', 'new', 'order', 'rfqs', 'relations', 'training', 'policies', 'procedures', 'act', 'level', …]
// location
// "Irvine, CA "
// mode
// "On-site"
// overallRating
// 3.2
// paymentBase
// 23.25
// paymentFreq
// "hr"
// paymentHigh
// 34.75
// secondsPostedAgo
// 0
// seniorManagementRating
// 2.8
// workLifeBalanceRating
// 2.6
const DB_NAME = "RECENT_JOBS_DB";

class JobDatabases {
    //Check if a job exists
    static exists(){
        //Asynchronously check
        return new Promise((resolve, reject) => {
            let request = indexedDB.open(DB_NAME, 1);
            //random error
            request.onerror = function(event) {
                console.error("Error opening database:", event.target.errorCode);
                reject(event.target.result);
            };
            //Need to create it
            request.onupgradeneeded = function(event) {
                reject(event.target.result);
            }
            //we found it
            request.onsuccess = function(event) {
                resolve(event.target.result);
            }
        })
    }
    static compressKeywords(keywords) {
        keywordStr = listOfStrings.join(" ");

        function compressStringGzip(input) {
            let binaryString = pako.gzip(input, { to: 'string' });
            return btoa(binaryString);
        }

        return compressStringGzip(keywordStr);
    }
    static decompressKeywords(compressedStr) {

        function decompressStringGzip(compressed) {
            let binaryString = atob(compressed);
            let decompressed = pako.ungzip(binaryString, { to: 'string' });
            return decompressed;
        }
        
        return decompressStringGzip(compressedStr);
    }
    static handleCreateDb(event) {
        console.log("HANDLING CREATE JOB DB EVENT");
        let db = event.target.result;
        if (!db.objectStoreNames.contains(DB_NAME)) {
            let objectStore = db.createObjectStore(DB_NAME, { keyPath: "jobId" });
            objectStore.createIndex("applicants", "applicants", { unique: false });
            objectStore.createIndex("businessOutlookRating", "businessOutlookRating", { unique: false });
            objectStore.createIndex("careerOpportunitiesRating", "careerOpportunitiesRating", { unique: false });
            objectStore.createIndex("careerStage", "careerStage", { unique: false });
            objectStore.createIndex("ceoRating", "ceoRating", { unique: false });
            objectStore.createIndex("company", "company", { unique: false });
            objectStore.createIndex("compensationAndBenefitsRating", "compensationAndBenefitsRating", { unique: false });
            objectStore.createIndex("cultureAndValuesRating", "cultureAndValuesRating", { unique: false });
            objectStore.createIndex("diversityAndInclusionRating", "diversityAndInclusionRating", { unique: false });
            objectStore.createIndex("job", "job", { unique: false });
            // TO DO implement
            // we compress the keywords before we add them and cut it to the top 15
            objectStore.createIndex("keywords", "keywords", { unique: false });
            objectStore.createIndex("location", "location", { unique: false });
            objectStore.createIndex("mode", "mode", { unique: false });
            objectStore.createIndex("overallRating", "overallRating", { unique: false });
            objectStore.createIndex("paymentBase", "paymentBase", { unique: false });
            objectStore.createIndex("paymentFreq", "paymentFreq", { unique: false });
            objectStore.createIndex("paymentHigh", "paymentHigh", { unique: false });
            objectStore.createIndex("secondsPostedAgo", "secondsPostedAgo", { unique: false });
            objectStore.createIndex("seniorManagementRating", "seniorManagementRating", { unique: false });
            objectStore.createIndex("workLifeBalanceRating", "workLifeBalanceRating", { unique: false });
            objectStore.createIndex("timeAdded", "timeAdded", { unique: false });
    
            console.log("Database setup updated");
        } else {
            console.log("Database already exists");
        }
        return db;
    }
    static openDatabase() {
        return new Promise((resolve, reject) => {
            let request = indexedDB.open(DB_NAME);

            request.onsuccess = function(event) {
                let db = event.target.result;
                resolve(db);
            };
            request.onupgradeneeded = function(event) {
                let db = JobDatabases.handleCreateDb(event);
                resolve(db);
            };
            request.onerror = function(event) {
                reject(event.target.errorCode);
            };
        });
    }
    static addNewJob(jobJson) {
        JobDatabases.openDatabase()
        .then((db) => {
            // Add a timestamp
            jobJson["timeAdded"] = new Date().toISOString();
            const transaction = db.transaction([DB_NAME], "readwrite");
            const objectStore = transaction.objectStore(DB_NAME);
    
            // Make a request to add the object
            let request = objectStore.add(jobJson);
    
            request.onsuccess = (event) => {
                // Report the success of our request
                console.log("successfully added job with ID: " + jobJson["jobId"]);
            };
    
            // Handle transaction completion
            transaction.oncomplete = () => {
                console.log("Transaction completed successfully.");
                db.close();  // Close the database if necessary
            };
    
            // Handle transaction error
            transaction.onerror = (event) => {
                console.error("Transaction error: ", event.target.error);
            };
        })
        .catch((err) => {
            console.log("Received an error trying to add job: " + err);
        });
    }
    static readMostRecentJob() {
        return new Promise((resolve, reject) => {
            JobDatabases.openDatabase()
            .then((db) => {
                const transaction = db.transaction([DB_NAME], "readonly");
                const objectStore = transaction.objectStore(DB_NAME);
    
                // Create a cursor request to get all items in descending order of timeAdded
                const index = objectStore.index("timeAdded");
                const request = index.openCursor(null, "prev"); // "prev" for descending order
    
                let mostRecentJob = null;
    
                request.onsuccess = (event) => {
                    console.log("Get most")
                    const cursor = event.target.result;
                    if (cursor) {
                        // First cursor result will be the most recent due to "prev" ordering
                        mostRecentJob = cursor.value;
                        cursor.continue(); // Continue to next item
                    } else {
                        // Resolve with the most recent job found
                        resolve(mostRecentJob);
                    }
                };
    
                transaction.onerror = (event) => {
                    console.error("Transaction error:", event.target.error);
                    reject(event.target.error);
                };
            })
            .catch((err) => {
                console.error("Error in readMostRecentJob:", err);
                reject(err);
            });
        });
    }
    static deleteJobById(jobId) {
        return new Promise((resolve, reject) => {
            JobDatabases.openDatabase()
            .then((db) => {
                const transaction = db.transaction([DB_NAME], "readwrite");
                const objectStore = transaction.objectStore(DB_NAME);
    
                // Use delete method to remove the job by jobId
                const deleteRequest = objectStore.delete(jobId);
    
                deleteRequest.onsuccess = (event) => {
                    console.log(`Job with ID ${jobId} deleted successfully`);
                    db.close();
                    resolve();
                };
    
                transaction.onerror = (event) => {
                    console.error(`Error deleting job with ID ${jobId}:`, event.target.error);
                    reject(event.target.error);
                };
    
                // Optional: Close transaction when done (automatically done after success)
                transaction.oncomplete = () => {
                    console.log("Transaction completed: job deleted");
                };
            })
            .catch((error) => {
                console.error(`Error deleting job with ID ${jobId}:`, error);
                reject(error);
            });
        });
    }
    static updateJobById(jobDataJson) {
        return new Promise((resolve, reject) => {
            const jobId = jobDataJson.jobId;
    
            JobDatabases.openDatabase()
            .then((db) => {
                const transaction = db.transaction([DB_NAME], "readwrite");
                const objectStore = transaction.objectStore(DB_NAME);
    
                // Retrieve existing job by jobId
                const getRequest = objectStore.get(jobId);
    
                getRequest.onsuccess = (event) => {
                    const existingJob = event.target.result;
                    if (!existingJob) {
                        reject(`Job with ID ${jobId} not found`);
                        return;
                    }
    
                    // Update existing job with jobDataJson
                    Object.assign(existingJob, jobDataJson);
    
                    // Put the updated job back into the object store
                    const updateRequest = objectStore.put(existingJob);
    
                    updateRequest.onsuccess = (event) => {
                        console.log(`Job with ID ${jobId} updated successfully`);
                        resolve();
                    };
    
                    updateRequest.onerror = (event) => {
                        console.error(`Error updating job with ID ${jobId}:`, event.target.error);
                        reject(event.target.error);
                    };
                };
    
                transaction.onerror = (event) => {
                    console.error(`Transaction error updating job with ID ${jobId}:`, event.target.error);
                    reject(event.target.error);
                };
    
                // Optional: Close transaction when done (automatically done after success)
                transaction.oncomplete = () => {
                    db.close();
                    console.log("Transaction completed: job updated");
                };
            })
            .catch((error) => {
                console.error(`Error updating job with ID ${jobId}:`, error);
                reject(error);
            });
        });
    }
}

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
const pako = require('pako');
const ORGINAL_DB_NAME = "RECENT_JOBS_DB";

class JobDatabases {
    //Check if a job exists
     exists(){
        //Asynchronously check
        return new Promise((resolve, reject) => {
            let request = indexedDB.open("BasketballDB", 1);
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
    compressKeywords(keywords) {
        keywordStr = listOfStrings.join(" ");

        function compressStringGzip(input) {
            let binaryString = pako.gzip(input, { to: 'string' });
            return btoa(binaryString);
        }

        return compressStringGzip(keywordStr);
    }
    decompressKeywords(compressedStr) {

        function decompressStringGzip(compressed) {
            let binaryString = atob(compressed);
            let decompressed = pako.ungzip(binaryString, { to: 'string' });
            return decompressed;
        }
        
        return decompressStringGzip(compressedStr);
    }
    handleCreateDb(event){
        let db = event.target.result;
        if (!db.objectStoreNames.contains(ORGINAL_DB_NAME)) {
            let objectStore = db.createObjectStore(ORGINAL_DB_NAME, { keyPath: "jobId"});
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
            //we compress the keywords before we add them and cut it to the top 15
            objectStore.createIndex("compressedKeywords", "keywords", { unique: false });
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
            return db;
        }
        console.log("Database alreadt exists");
        return db;
    }
    openDatabase() {
        return new Promise((resolve, reject) => {
            let request = indexedDB.open(ORGINAL_DB_NAME);

            request.onsuccess = function(event) {
                let db = event.target.result;
                resolve(db);
            };
            request.onupgradeneeded = function(event) {
                let db = handleCreateDb(event);
                resolve(db);
            };
            request.onerror = function(event) {
                reject(event.target.errorCode);
            };
        });
    }
    addNewJob(jobJson) {
        //compress the keywords
        jobJson["keywords"] = JobDatabases.compressKeywords(jobJson["keywords"])
        //add a timestamp
        jobJson["timeAdded"] = new Date().toISOString()
        let request = objectStore.add(jobJson);
        request.onsuccess = function(event) {
          resolve(event.target.result);
        };
        request.onerror = function(event) {
          reject(event.target.errorCode);
        };
    }
}
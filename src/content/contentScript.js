(() => {
    let currentJob = "";
    chrome.runtime.onMessage.addListener((obj, sender, response) => {
        console.log("Message recieved");
        const { type, value, jobId } = obj;

        if (type === "NEW") {
            currentJob = jobId;
            console.log(jobId);
            newJobLoaded();
        }
    });

        // Common stopwords to exclude
    const stopwords = [
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", 
        "into", "is", "it", "of", "on", "or", "that", "the", "to", "with", "will",
        "firm", "about", "our", "their", "team", "role", "process", "through",
        "day", "regional", "well", "can", "please", "including", "individual", "work",
        "benefits", "we", "job", "company", "select", "review", "stakeholders", "plan",
        "services", "products", "qualifications", "what", "you", "other"
    ];

    // Function to extract keywords
    function extractKeywords(text) {
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
    const getTopBoxInfoData = (topBox) => {
        topBoxText = topBox.textContent.trim();
        topBoxContents = topBoxText.split("·");
        console.log(topBoxContents);
        topBoxData = {
            "location": "",
            "secondsPostedAgo": 0,
            "applicants": 0
        };
        topBoxData["location"] = topBoxContents[0];
        console.log("Location: " + topBoxContents[0])
        timeComponents = topBoxContents[1].split(" ").filter(element => element !== "");
        console.log(timeComponents);
        numberOfTimeframe = timeComponents[0];
        timeFrame = timeComponents[1];
        console.log("Timeframe: " + timeFrame)
        switch (timeFrame) {
            case 'months':
                topBoxData["secondsPostedAgo"] = 7 * 24 * 3600;
                break;
            case 'month':
                topBoxData["secondsPostedAgo"] = 7 * 24 * 3600;
                break;
            case 'weeks':
                topBoxData["secondsPostedAgo"] = 7 * 24 * 3600;
                break;
            case 'week':
                topBoxData["secondsPostedAgo"] = 7 * 24 * 3600;
                break;
            case 'days':
                topBoxData["secondsPostedAgo"] = 24 * 3600;
                break;
            case 'day':
                topBoxData["secondsPostedAgo"] = 24 * 3600;
                break;
            case 'hours':
                topBoxData["secondsPostedAgo"] = 3600;
                break;
            case 'hour':
                topBoxData["secondsPostedAgo"] = 3600;
                break;
            case 'minutes':
                topBoxData["secondsPostedAgo"] = 60;
                break;
            case 'minute':
                topBoxData["secondsPostedAgo"] = 60;
                break;
            default:
                console.error('Unsupported timeframe');
                break;
        }
        applicantStr = topBoxContents[2];
        const numbers = applicantStr.split(" ").filter(str => !isNaN(str));
        topBoxData["applicants"] = numbers[0];
        console.log("Applicants: " + numbers[0]);
        return topBoxData;
    }
    const getJobInfoData = (descriptionBox) => {
        descriptionBoxText = descriptionBox.textContent.trim();
        descriptionBoxContents = descriptionBoxText.split("\n");
        
        descriptionData = {
            "paymentFreq": "",
            "paymentBase": "",
            "paymentHigh": "",
            "mode": "",
            "careerStage": ""
        };

        modes = ["Remote", "Hybrid", "On-site"],
        careerStages = ["Associate", "Entry level", "Mid-Senior level", "Executive", "Director", ]
        for (let element of descriptionBoxContents){
            str = String(element);
            for (let mode of modes){
                if (str.includes(mode)){
                    descriptionData["mode"] = mode;
                    console.log("found mode of " + mode); 
                    continue;
                }
            };
            for (let careerStage of careerStages){
                if (str.includes(careerStage)){
                    descriptionData["careerStage"] = careerStage;
                    console.log("found careerStage of " + mode); 
                    continue;
                }
            };
            if (str.includes("$")){
                if (str.includes("yr")){
                    descriptionData["paymentFreq"]  = "yr";
                }
                if (str.includes("hr")){
                    descriptionData["paymentFreq"]  = "hr";
                }
                const regex = /[\d,]+\.?\d*/g;
                const matches = str.match(regex);
                
                if (matches) {
                    // Convert matched strings to numbers and return as an array
                     amounts = matches.map(match => parseFloat(match.replace(/,/g, '')));
                     descriptionData["paymentBase"] = amounts[0];
                     if (amounts.length < 2){
                        continue;
                     }
                     descriptionData["paymentHigh"] = amounts[1];
                }
            }
        };
        return descriptionData;
    };

    const newJobLoaded = () => {
        console.log("New Job Loaded");
        //use document methods here to grab the info we need
        companyNameBox = document.getElementsByClassName("job-details-jobs-unified-top-card__company-name")[0];
    
        if (companyNameBox) {
            let company = companyNameBox.textContent.trim();
            console.log("Company: " + company);
        } else {
            console.log("Company name box not found");
        }

        jobNameBox = document.getElementsByClassName("job-details-jobs-unified-top-card__job-title")[0];

        if (jobNameBox) {
            let job = jobNameBox.textContent.trim();
            console.log("Job: " + job);
        } else {
            console.log("Job name box not found");
        }

        //holds salary, on site hybrid remote, 
        infoBox = document.getElementsByClassName("job-details-jobs-unified-top-card__job-insight")[0];
        topBox = document.getElementsByClassName("job-details-jobs-unified-top-card__primary-description-container")[0];
        if (!infoBox) {
            console.log("description_box_text not found");
        }
        if (!topBox) {
            console.log("top_box_text not found");
        }
        topBoxData = getTopBoxInfoData(topBox);
        descriptionData = getJobInfoData(infoBox);
        console.log(descriptionData);
        console.log(topBoxData);
        jobDescriptionBox = document.getElementById("job-details");

        jobDescriptionText = jobDescriptionBox.textContent.trim();

        // Extract keywords from the job description
        const keywords = extractKeywords(jobDescriptionText);

        // Print the keywords
        console.log(keywords);
    }
    newJobLoaded();
})();

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

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

//SERVER SIDE

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
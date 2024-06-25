sendMessageToGetLocation = (jobDataJson) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our database program runs on port 5001 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        xhr.open('GET', 'http://localhost:5002/google_places/address?company=' + encodeURIComponent(jobDataJson["company"]) + "&locationStr=" + encodeURIComponent(jobDataJson["location"]), true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = JSON.parse(xhr.responseText);
                console.log("Request Suceeded");
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
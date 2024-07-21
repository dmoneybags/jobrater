/*
Execution flow:

ContentScript:
Scrapes page for current job
\/
\/
databaseCalls
Is called to validate if the company data already exists in our db 
is called to add company/job to db

SignUp.html
\/
\/
databaseCalls
is called to validate if a user already exists 
returns tokens
adds new users to db
*/

databaseServer = 'http://localhost:5001/'

//This function simply checks if the company exists by 
//querying our db
const checkIfCompanyExists = (company) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our python program runs on port 5000 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        console.log("Sending Request to get company");
        xhr.open('GET', databaseServer + 'databases/read_company?company=' + encodeURIComponent(company), true);
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
const sendMessageToAddJob = (jobJson) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our database program runs on port 5001 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        xhr.open('POST', databaseServer + 'databases/add_job?jobJson=' + encodeURIComponent(JSON.stringify(jobJson)), true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = xhr.responseText;
                console.log("Add Job Request Suceeded");
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
const getUserData = () => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our database program runs on port 5001 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        //No args, uses the users token
        xhr.open('POST', databaseServer + 'databases/get_user_data', true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = xhr.responseText;
                console.log("Read user data of " + response);
                resolve(JSON.parse(response));
            } else if (xhr.status === 404){
                //We didnt find the user in the db
                console.log("User with email " + email + " not found in db");
                resolve(null)
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
}
const getUserByGoogleId = (googleId) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our database program runs on port 5001 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        xhr.open('POST', databaseServer + 'databases/get_user_by_googleId?googleId=' + encodeURIComponent(googleId), true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = xhr.responseText;
                console.log("Read user with the googleId of " + googleId);
                resolve(JSON.parse(response));
            } else if (xhr.status === 404){
                //We didnt find the user in the db
                console.log("User with googleId " + googleId + " not found in db");
                resolve(null)
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
}
const sendMessageToAddUser = (userJson) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our database program runs on port 5001 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        xhr.open('POST', databaseServer + 'databases/user=' + encodeURIComponent(JSON.stringify(userJson)), true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = xhr.responseText;
                resolve(response)
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
}
const sendMessageToDeleteUser = (user) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our python program runs on port 5007 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        //we do NOT add any args, the token tells it which user to delete
        xhr.open('POST', databaseServer + 'databases/delete_user', true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = xhr.responseText;
                console.log(response)
                //resolve the token
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
}
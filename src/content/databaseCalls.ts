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
import { UserFactory, User } from "./user";
import { Job, JobFactory } from "./job"

const DATABASESERVER = 'http://localhost:5001/'
export class DatabaseCalls{
    /**
     * checkIfCompanyExists
     * 
     * Asychronously queries our db to check if a company has already been scraped
     * 
     * @param {string} company: the string company name we are checking
     * @returns {Promise<boolean>}: will resolve to true or false depending on if the company exists
     */
    static checkIfCompanyExists = (company: string):Promise<boolean> => {
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our python program runs on port 5000 on our local server
            var xhr: XMLHttpRequest = new XMLHttpRequest();
            //call an http request
            console.log("Sending Request to get company");
            xhr.open('GET', DATABASESERVER + 'databases/read_company?company=' + encodeURIComponent(company), true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status == 200){
                    console.log("Recieved the company from the db");
                    resolve(true);
                } else {
                    resolve(false);
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
    /**
     * sendMessageToAddJob
     * 
     * we send our jobjson to server and server adds it to db and sends it back with all fk data
     * 
     * @param {Job} job
     * @returns {Promise<Record<string, any>>} contains the finished job under the "job" keyword
     */
    static sendMessageToAddJob = (job: Job):Promise<Record<string, any>> => {
        const jobJson: Record<string, any> = job.toJson();
        console.log("Sending message to add job");
        console.log(jobJson);
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our database program runs on port 5001 on our local server
            var xhr = new XMLHttpRequest();
            //call an http request
            xhr.open('POST', DATABASESERVER + 'databases/add_job?jobJson=' + encodeURIComponent(JSON.stringify(jobJson)), true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status === 200) {
                    //change it to json
                    var response: string = xhr.responseText;
                    const responseJson: Record<string, any> = JSON.parse(response);
                    console.log("Add Job Request Suceeded");
                    resolve(responseJson);
                } else {
                    //Didnt get a sucessful message
                    console.log('Request failed. Status:', xhr.status);
                    reject(String(xhr.status));
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(String(xhr.status));
            };
            //send our response
            xhr.send();
        });
    };
    /**
     * getUserData
     * 
     * Gets user data from db using the token to identify the user
     * 
     * @returns {Promise<Record<string, any>>} user and jobs
     */
    static getUserData = (): Promise<Record<string, any>> => {
        return new Promise((resolve, reject) => {
            const xhr: XMLHttpRequest = new XMLHttpRequest();
            xhr.open('GET', `${DATABASESERVER}databases/get_user_data`, true);
            xhr.onload = () => {
                if (xhr.status === 200) {
                    try {
                        const response: Record<string, any> = JSON.parse(xhr.responseText);
                        console.log(`Read user data of ${xhr.responseText}`);
                        const jsonJobs: Record<string, any>[] = response["jobs"];
                        const jobs : Job[] = jsonJobs.map((job) => JobFactory.generateFromJson(job));
                        resolve({
                            user: UserFactory.generateFromJson(response["user"]),
                            jobs: jobs
                        });
                    } catch (error) {
                        console.error('Error parsing JSON response', error);
                        console.log(xhr.responseText);
                        reject(new Error('Invalid JSON response'));
                    }
                } else if (xhr.status === 404) {
                    console.log('User not found in db');
                    reject(new Error(`User not found`));
                } else {
                    console.error(`Request failed. Status: ${xhr.status}`);
                    reject(new Error(`Request failed with status ${xhr.status}`));
                }
            };
    
            xhr.onerror = () => {
                console.error('Request failed. Network error');
                reject(new Error('Network error'));
            };
    
            xhr.send();
        });
    };
    /**
     * getUserByGoogleId
     * 
     * Grabs user from our db based by their google id
     * 
     * @param {string} googleId - the google id of the user
     * @returns {Promise<User>}
     */
    static getUserByGoogleId = (googleId: string):Promise<User> => {
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our database program runs on port 5001 on our local server
            var xhr = new XMLHttpRequest();
            //call an http request
            xhr.open('POST', DATABASESERVER + 'databases/get_user_by_googleId?googleId=' + encodeURIComponent(googleId), true);
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
                    reject(new Error(`googleId of ` + googleId + "not found in db"));
                } else {
                    //Didnt get a sucessful message
                    console.error('Request failed. Status:', xhr.status);
                    reject(new Error("Got bad status of " + xhr.status));
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(new Error("Got bad status of " + xhr.status));
            };
            //send our response
            xhr.send();
        });
    }
    /**
     * sendMessageToAddUser
     * 
     * sends message to add user. Will error anytime user could not be added to db. Returns a fully useless success
     * string 
     * 
     * @param {user} user - user object we are attempting to add
     * @returns {Promise<string>} - will just be success if we got it, everything else is an error
     */
    static sendMessageToAddUser = (user: User):Promise<string> => {
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our database program runs on port 5001 on our local server
            var xhr = new XMLHttpRequest();
            //call an http request
            xhr.open('POST', DATABASESERVER + 'databases/user=' + encodeURIComponent(JSON.stringify(user)), true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status === 200) {
                    //change it to json
                    var response: string = xhr.responseText;
                    resolve(response)
                } else {
                    //Didnt get a sucessful message
                    console.error('Request failed. Status:', xhr.status);
                    reject(new Error("Got bad status of " + xhr.status));
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(new Error("Got bad status of " + xhr.status));
            };
            //send our response
            xhr.send();
        });
    }
    /**
     * sendMessageToDeleteUser
     * 
     * sends message to delete user. The user is loaded from the token
     * 
     * @returns {Promise<string>}
     */
    static sendMessageToDeleteUser = ():Promise<string> => {
        //create a promise to resolve it asynchronously
        return new Promise((resolve, reject) => {
            //Our python program runs on port 5007 on our local server
            var xhr = new XMLHttpRequest();
            //call an http request
            //we do NOT add any args, the token tells it which user to delete
            xhr.open('POST', DATABASESERVER + 'databases/delete_user', true);
            xhr.onload = function () {
                //It suceeded
                if (xhr.status === 200) {
                    //change it to json
                    var response: string = xhr.responseText;
                    console.log(response)
                    //resolve the token
                    resolve(response);
                } else {
                    //Didnt get a sucessful message
                    console.error('Request failed. Status:', xhr.status);
                    reject(new Error("Got bad status of " + xhr.status));
                }
            };
            //Couldnt load the http request
            xhr.onerror = function () {
                console.error('Request failed. Network error');
                reject(new Error("Got bad status of " + xhr.status));
            };
            //send our response
            xhr.send();
        });
    }
}
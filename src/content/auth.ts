/*
Execution flow:

signup.html
\/
\/
auth.js

need to:

register user
-validate user data
-send message to attempt to register user
-set token once we get it
-set active user
login user
-send message to login user
-set token once we get it
-set active user

set token X
add token to headers X
set active user X

*/

import { User, UserFactory } from "./user"
import { LocalStorageHelper } from "./localStorageHelper"

//Base url for our authentification server
const authServer: string = 'http://localhost:5007/'

/**
 * getSalt
 * 
 * Gets salt for a users password hash before authing with server
 * 
 * @example control flow:
 * 
 * 1. User enters email, send request to get salt
 * 2. if salt is found show login screen, if not ask to register
 * 
 * @param email: string email of user
 * @returns promise which resolves to the salt and rejects to null if we get a 404
 */
const getSalt = (email: string): Promise<string | null> => {
    return new Promise((resolve, reject) => {
        sendGetSaltMsg(email)
        .then((salt) => {
            resolve(salt);
        })
        .catch((responseCode) => {
            if (responseCode === "404"){
                console.log("Failed to get salt for email: " + email);
                reject(null);
            }
            throw new Error(`Unexpected response code: ${responseCode}`)
        })
    })
}
/**
 * sendGetSaltMsg
 * 
 * Sends message to retrieve salt based on users email. Same as getSalt but contains no error handling
 * 
 * @param {string} email the string email of the user whose salt we are looking up
 * @returns {Promise<string>} resolves to salt, rejects to http code
 */
const sendGetSaltMsg = (email: string):Promise<string> => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our python program runs on port 5007 on our local server
        var xhr: XMLHttpRequest = new XMLHttpRequest();
        //call an http request
        xhr.open('GET', authServer + 'get_salt_by_email?email=' + encodeURIComponent(email), true);
        xhr.setRequestHeader('Content-type', 'application/json');
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response: Record<string, any> = JSON.parse(xhr.responseText);
                console.log(response)
                //resolve the salt
                resolve(response["salt"]);
            } else {
                //Didnt get a sucessful message
                console.error('Request failed. Status:', xhr.status);
                reject(String(xhr.status));
            }
        };
        //Couldnt load the http request
        xhr.onerror = function () {
            //TODO handle this error in getSalt
            console.error('Request failed. Network error');
            reject(xhr.status);
        };
        //send our response
        xhr.send();
    });
}
/**
 * sendRegisterMsg
 * 
 * sends a xhr request to register a user. Resolves json of token given to the user and the user_id delegated to
 * user, rejects string response code
 * 
 * @param {User} user the user object we are attempting to register 
 * @param {string} salt the string salt we are using to hash password before sending it to server
 * @returns {Promise<string>} resolves to json with token and user_id and rejects to the string response code
 */
const sendRegisterMsg = (user: User, salt: string):Promise<string | Record<string, any>> => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our python program runs on port 5007 on our local server
        var xhr: XMLHttpRequest = new XMLHttpRequest();
        //call an http request
        xhr.open('POST', authServer + 'register?user=' + encodeURIComponent(JSON.stringify(user)) + '&' + 'salt=' + encodeURIComponent(salt), true);
        xhr.setRequestHeader('Content-type', 'application/json');
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response: Record<string, any> = JSON.parse(xhr.responseText);
                console.log(response)
                //resolve the token
                resolve(response);
            } else {
                //Didnt get a sucessful message
                console.error('Request failed. Status:', xhr.status);
                reject(String(xhr.status));
            }
        };
        //Couldnt load the http request
        xhr.onerror = function () {
            console.error('Request failed. Network error');
            reject(xhr.status);
        };
        //send our response
        xhr.send();
    });
}
/**
 * sendLoginMsg
 * 
 * sends message to login a user without any error handling and such. Very basic
 * 
 * @param {string} email: string email of the user
 * @param {string} password: !IMPORTANT password should already be encrypted with salt. Run getSalt and bcrypt it
 * before login
 * @returns {Promise<string>} resolves to {'token': token, 'user': user.to_json()} rejects to a 401 for invalid user
 */
const sendLoginMsg = (email: string, password: string):Promise<string | Record<string, any>> => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our python program runs on port 5007 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        xhr.open('POST', authServer + 'login?email=' + encodeURIComponent(email) + "&" + "password="+ encodeURIComponent(password), true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response: Record<string, any> = JSON.parse(xhr.responseText);
                console.log(response)
                //resolve the token
                resolve(response);
            } else {
                //Didnt get a sucessful message
                console.error('Request failed. Status:', xhr.status);
                reject(String(xhr.status));
            }
        };
        //Couldnt load the http request
        xhr.onerror = function () {
            console.error('Request failed. Network error');
            reject(xhr.status);
        };
        //send our response
        xhr.send();
    });
}
/**
 * register
 * 
 * Main function to register the user
 * 
 * Salt is needed to hash the password before sending the request
 * 
 * @param {User} user: the user object we are attempting to register
 * @param {string} salt: the string salt of the user that we add to the password before we hash
 * @returns {Promise<string>}
 */
const register = (user: User, salt: string) => {
    return new Promise((resolve, reject) => {
        sendRegisterMsg(user, salt)
            .then((response) => {
                LocalStorageHelper.setToken(response["token"]);
                user.userId = response["userId"];
                LocalStorageHelper.setActiveUser(user);
                resolve("Success");
            })
            .catch((error) => {
                console.log("FAILED TO REGISTER USER WITH ERROR: " + error)
                reject(error);
            })
    })
}
/**
 * login
 * 
 * main function to login the user, rejects if we recieve an http error.
 * 
 * Resolves just "success" not too useful but sets the active user and token
 * 
 * @param {string} email: email of the user
 * @param {string} password: !IMPORTANT hashed password of user
 * @param {number} attempts: number of times we've attempted to login
 * @returns {Promise<string>} resolves successs rejects bad err code
 */
const login = (email: string, password: string, attempts: number = 0) => {
    return new Promise((resolve, reject) => {
        sendLoginMsg(email, password)
            .then((response) => {
                console.log(response);
                LocalStorageHelper.setToken(response["token"])
                //User is a string from the response
                const userJson: Record<string, any> = response["user"];
                const user = UserFactory.generateFromJson(userJson);
                LocalStorageHelper.setActiveUser(user);
                resolve("Success");
            })
            //catch in all these functions will catch the error code
            //0 is network error
            .catch((error) => {
                console.warn("ERROR RECIEVED ATTEMPTING LOGIN: " + error);
                reject(error);
            })
    })
}
//Overriding the xml open function to add our auth token to every request
(function() {
    const originalOpen = XMLHttpRequest.prototype.open;
    const authToken = LocalStorageHelper.getToken();

    XMLHttpRequest.prototype.open = function(method: string, url: string, async?: boolean, user?: string, password?: string) {
        this.addEventListener('readystatechange', function() {
            if (this.readyState === XMLHttpRequest.OPENED) {
                this.setRequestHeader('Authorization', authToken);
            }
        });
        originalOpen.apply(this, arguments as unknown as [string, string, boolean?, string?, string?]);
    };
})();
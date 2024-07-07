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
const setToken = (token) => {
    localStorage.setItem("authToken", token)
}
const getToken = () => {
    return localStorage.getItem("authToken")
}
const setActiveUser = (user) => {
    localStorage.setItem("activeUser", JSON.stringify(user))
}
const getActiveUser = () => {
    return JSON.parse(localStorage.getItem("activeUser"))
}
const encryptPassword = (user) => {

}
//Sends a message to the auth server to register user and handles exceptions on the way
//ARGS: user object
//returns: Promise(token, error message)
const sendRegisterMsg = (user) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our python program runs on port 5007 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        xhr.open('POST', 'http://localhost:5007/register?user=' + encodeURIComponent(JSON.stringify(user)), true);
        xhr.setRequestHeader('Content-type', 'application/json');
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = JSON.parse(xhr.responseText);
                console.log(response)
                //resolve the token
                resolve(response["token"]);
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
//Sends a message to the auth server to register user and handles exceptions on the way
//ARGS: user object
//returns: Promise(token, error message)
//NOTE PASSWORD SHOULD ALREADY BE ENCRYPTED AT THIS POINT
const sendLoginMsg = (email, password) => {
    //create a promise to resolve it asynchronously
    return new Promise((resolve, reject) => {
        //Our python program runs on port 5007 on our local server
        var xhr = new XMLHttpRequest();
        //call an http request
        xhr.open('POST', 'http://localhost:5007/login?email=' + encodeURIComponent(email) + "&" + "password="+ encodeURIComponent(password), true);
        xhr.onload = function () {
            //It suceeded
            if (xhr.status === 200) {
                //change it to json
                var response = JSON.parse(xhr.responseText);
                console.log(response)
                //resolve the token
                resolve(response["token"]);
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
//Register function, called after a user enters all their data on the sign up screen
//We should already know if the user is in our db but still checks for this and validates
//the user data
//ARGS: user, JSON representation of user
//Returns: Promise(success, error)
//TO DO: must encrypt password before it is sent to server
const register = (user) => {
    return new Promise((resolve, reject) => {
        sendRegisterMsg(user)
            .then((token) => {
                setToken(token)
                setActiveUser(user)
                resolve("Success")
            })
            .catch((error) => {
                console.log("FAILED TO REGISTER USER WITH ERROR: " + error)
            })
    })
}
//login function, called after a user enters all their data on the login screen
//ARGS: user, JSON representation of user
//Returns: Promise(success, error)
//TO DO: must encrypt password before it is sent to server
const login = (user) => {
    return new Promise((resolve, reject) => {
        sendLoginMsg(user)
            .then((token) => {
                setToken(token)
                setActiveUser(user)
                resolve("Success")
            })
            .catch((error) => {
                console.log("FAILED TO LOGIN USER WITH ERROR: " + error)
            })
    })
}
//Overriding the xml open function to add our auth token to every request
(function() {
    const originalOpen = XMLHttpRequest.prototype.open;
    const authToken = getToken();
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        this.addEventListener('readystatechange', function() {
            if (this.readyState === XMLHttpRequest.OPENED) {
                this.setRequestHeader('Authorization', authToken);
            }
        });
        originalOpen.apply(this, arguments);
    };
})();
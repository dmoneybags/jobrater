import React, { createElement } from 'react';
import ReactDOM from 'react-dom';
import {genSaltSync, hashSync} from 'bcryptjs';
import {createUser} from '../content/users';
import { User } from '../content/user';

//Tests to test our methods to call the servers and the server methods themselves
//will add fakerjs eventually
//db must be cleared at the start to avoid duplicant adds
let jobData = null

fetch('/src/tests/testJob.json')
    .then((response) => response.json())
    .then((json) => jobData = json);

function assert(condition, message) {
    if (!condition) {
        throw new Error(message || "Assertion failed");
    }
}

//Auth tests

//test that a proper user can register
async function registerTest(){
    let salt = genSaltSync();
    let password = "Blorgnine27#"
    //random data for cryptography
    //to do: key exchange or store salt in db
    const email = "dandemoney@gmail.com"
    //we do this here as soon as possible for password safety
    const confirmPassword = password;
    //create user returns the proper user json structure with null filled values
    const firstName = "Daniel";
    const lastName = "DeMoney";
    const userJson = {
        email: email,
        firstName: firstName,
        lastName: lastName,
        password: password,
        salt: salt
    }
    const user = new User("", email, null, firstName, lastName, null);
    const validationData = validateUserDataObject(userJson, confirmPassword);
    if (!validationData.isValid){
        console.log("INVALID REGISTRATION DATA " + validationData.message);
        assert(false, "INVALID REGISTRATION DATA FOR WHAT SHOULD BE A PROPER USER");
        return;
    }
    user.password = hashSync(user.password, salt);
    //We must pass the salt because it needs to be stored in our db
    await register(user, salt)
    .then(() => {
        console.log("Register suceeded")
        console.log("------PROPER REGISTER TEST 1-----");
        const userRead = getActiveUser();
        //test that active user gets set
        console.log(userRead)
        assert(userRead !== null && userRead !== undefined);
        assert(userRead.firstName === "Daniel");
        console.log("first name matches")
        assert(userRead.userId !== null);
        console.log("userId grabbed")
        assert(userRead.email === email);
        console.log("email grabbed")
        console.log("USER CORRECTLY READ");
        console.log("GRABBING TOKEN")
        //test that token gets properly set
        const token = getToken();
        assert(token !== null && token !== undefined);
        console.log("TOKEN READ");
        console.log("------PROPER REGISTER TEST 1 PASSED-----");
    })
}
//test that a improper user can't register
async function registerTestNegativeDupEmail(){
    console.log("------NEGATIVE DUPLICATE EMAIL REGISTER TEST 1-----");
    let salt = genSaltSync();
    let password = "scooby-Dooby-DOO24%"
    //random data for cryptography
    //to do: key exchange or store salt in db
    const email = "gloobelGOB@hotmail.com"
    //we do this here as soon as possible for password safety
    const name = " I'm not Gloobel gob";
    const confirmPassword = password;
    //create user returns the proper user json structure with null filled values
    const user = createUser({email: email, name: name, password: password})
    const validationData = validateUserDataObject(user, confirmPassword);
    if (!validationData.isValid){
        console.log("INVALID REGISTRATION DATA " + validationData.message);
        assert(false, "INVALID REGISTRATION DATA FOR WHAT SHOULD BE A PROPER USER");
        return;
    }
    user.password = hashSync(user.password, salt);
    //We must pass the salt because it needs to be stored in our db
    console.log("Starting mock register test for duplicate user");
    await register(user, salt)
    .then(() => {
        console.log("Register response receieved, test FAILED");
        assert(false);
    })
    .catch((error) => {
        console.log("------NEGATIVE DUPLICATE EMAIL REGISTER TEST 1 PASSED-----");
    })
}
//test that an improper user can't
async function registerTestNegativeBadData(){
    console.log("------ TESTING NEGATIVE BAD DATA REGISTER TEST 1 ------");
    let salt = genSaltSync();
    let password = "scooby-Dooby-DOO"
    //random data for cryptography
    //to do: key exchange or store salt in db
    const email = "gloobelGOBhotmail.com"
    //we do this here as soon as possible for password safety
    const name = " I'm not Gloobel gob";
    const confirmPassword = password;
    //create user returns the proper user json structure with null filled values
    const user = createUser({email: email, name: name, password: password})
    const validationData = validateUserDataObject(user, confirmPassword);
    console.log("Starting mock register test for invalid user");
    if (!validationData.isValid){
        console.log("INVALID REGISTRATION DATA " + validationData.message);
        console.log("------ PASSED NEGATIVE BAD DATA REGISTER TEST 1 ------");
        return;
    }
    console.log("FAILED INVALID REGISTRATION DATA TEST");
    assert(false);
}
//test that a user in db can login
//test that active user and token get set
async function loginTest(){
    console.log("------ STARTING LOGIN TEST 1 ------");
    const emailValue = "dandemoney@gmail.com";
    await getSalt(emailValue)
    .then(async(salt) => {
        const passwordValue = "Blorgnine27#";
        const hashedPW = hashSync(passwordValue, salt);
        const user = createUser({email: emailValue, password: hashedPW})
        console.log("BEGINNING LOGIN USER TESTS");
        await login(user)
        .then(() =>{
            console.log("User successfully ")
            const userRead = getActiveUser();
            //test that active user gets set
            assert(userRead !== null && userRead !== undefined);
            assert(userRead.email === emailValue);
            console.log("USER CORRECTLY READ");
            //test that token gets properly set
            const token = getToken();
            assert(token !== null && token !== undefined);
            console.log("TOKEN READ");
            console.log("------ PASSED LOGIN TEST 1 ------");
        })
    })
}
//test that a user not in db can't 

//Token tests

//Test that request with good token works
async function testTryAddJob(){
    console.log("------ TESTING ADD JOB TEST 1 ------");
    console.log("ATTEMPTING TO ADD JOB FOR USER");
    await sendMessageToAddJob(jobData)
    .then((response) => {
        console.log("SUCCESSFULLY ADDED JOB WITH RESPONSE:");
        console.log(response);
        console.log("------ PASSED ADD JOB TEST 1 ------");
    })
    .catch((error) => {
        console.log("FAILED TO ADD JOB WITH ERROR:");
        console.log(error);
        assert(false);
    })
}
//test that request with bad token doesnt work
async function testTryAddJobNegative(){
    console.log("------ TESTING ADD JOB NEGATIVE TEST 1 ------");
    console.log("ATTEMPTING TO ADD JOB FOR USER WITH BAD TOKEN");
    setToken("DHGWIPGNVNWPEFI!#IRN##PI!NDSAINFASF");
    await sendMessageToAddJob(jobData)
    .then((response) => {
        console.log("NEGATIVE JOB TEST FAILED POOR TOKEN WORKED WITH RESP:")
        console.log(response);
        assert(false);
    })
    .catch((error) => {
        console.log("NEGATIVE TEST PROPERLY FAILED WITH ERROR:");
        console.log(error);
        console.log("------ PASSED ADD JOB NEGATIVE TEST 1 ------");
    })
}
//test that request with no token doesnt work
async function testTryAddJobNoToken(){
    console.log("------ TESTING ADD JOB NEGATIVE TEST 2 ------");
    console.log("ATTEMPTING TO ADD JOB FOR USER WITH BAD TOKEN");
    setToken("");
    await sendMessageToAddJob(jobData)
    .then((response) => {
        console.log("NEGATIVE JOB TEST FAILED POOR TOKEN WORKED WITH RESP:")
        console.log(response);
        assert(false);
    })
    .catch((error) => {
        console.log("NEGATIVE TEST PROPERLY FAILED WITH ERROR:");
        console.log(error);
        console.log("------ PASSED ADD JOB NEGATIVE TEST 2 ------");
    })
}
//test that token can get user from it
async function testTryDeleteUser(){
    console.log("------ TESTING DELETING USER TEST 1 ------");
    console.log("ATTEMPTING TO DELETE USER");
    console.log("RELOGGING IN USER");
    const emailValue = "dandemoney@gmail.com";
    await getSalt(emailValue)
    .then(async(salt) => {
        const passwordValue = "Blorgnine27#";
        const hashedPW = hashSync(passwordValue, salt);
        let user = createUser({email: emailValue, password: hashedPW})
        console.log("BEGINNING LOGIN USER TESTS");
        await login(user)
        .then(async() =>{
            let user = getActiveUser();
            await sendMessageToDeleteUser(user)
            .then((resp) => {
                console.log("SUCCESSFULLY GOT USER FROM TOKEN AND DELETED WITH RESP");
                console.log(resp);
                console.log("------ PASSED DELETING USER TEST 1 ------");
            })
            .catch((error) => {
                console.log("FAILED TO DELETE USER WITH ERROR: ");
                console.log(error);
                assert(false);
            })
        })
        .catch((error) => {
            console.log("DELETE USER TEST FAILED WITH ERROR: " + error);
            assert(false);
        });
    })
}
async function attemptToReloginUserAfterDelete(){
    console.log("------ TESTING NEGATIVE USER TEST 1 ------");
    console.log("ATTEMPTING TO LOGIN PREVIOUSLY DELETED USER");
    const emailValue = "gloobelGOB@hotmail.com";
    getSalt(emailValue)
    .then(async(salt) => {
        const passwordValue = "Blorgnine27#";
        const hashedPW = hashSync(passwordValue, salt);
        let user = createUser({email: emailValue, password: hashedPW})
        console.log("BEGINNING LOGIN USER TESTS");
        await login(user)
        .then(() =>{
            console.log("FAILED TEST, USER WAS ABLE TO LOGIN");
            assert(false);
        })
        .catch((error) => {
            console.log("LOGGING IN USER TEST PASSED WITH ERROR: " + error);
            console.log("------ PASSED NEGATIVE USER TEST 1 ------");
        });
    })
}

//MAIN:
async function runTests(){
    await registerTest();
    await registerTestNegativeDupEmail();
    await registerTestNegativeBadData();
    await loginTest();
    await testTryAddJob();
    await testTryDeleteUser();
    await attemptToReloginUserAfterDelete();
    //These two set tokens, if you need valid tokens run your tests before these
    //or regrab auth
    await testTryAddJobNoToken();
    await testTryAddJobNegative();
}

runTests();


import React, { createElement } from 'react';
import ReactDOM from 'react-dom';
import {genSaltSync, hashSync} from 'bcryptjs';
import {createUser} from '../users';

//Tests to test our methods to call the servers and the server methods themselves
//will add fakerjs eventually
//db must be cleared at the start to avoid duplicant adds
const RUNTESTS = false;
let jobData = null

fetch('/src/content/tests/testJob.json')
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
    const email = "gloobelGOB@hotmail.com"
    //we do this here as soon as possible for password safety
    const name = "Gloobel gob";
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
    await register(user, salt)
    .then(() => {
        console.log("Register suceeded")
        console.log("------PROPER REGISTER TEST 1-----");
        const userRead = getActiveUser();
        //test that active user gets set
        assert(userRead !== null && userRead !== undefined);
        assert(userRead.name === name);
        assert(userRead.userId !== null);
        assert(userRead.email === email);
        assert(!user.password);
        console.log("USER CORRECTLY READ");
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
    const emailValue = "gloobelGOB@hotmail.com";
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
    const emailValue = "gloobelGOB@hotmail.com";
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
    if (RUNTESTS){
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
}

runTests();

const testTryRegister = (event) => {
    event.preventDefault();
    let salt = genSaltSync();
    let password = document.getElementById("registerPassword").value;
    //random data for cryptography
    //to do: key exchange or store salt in db
    const email = document.getElementById("registerEmail").value;
    //we do this here as soon as possible for password safety
    const name = document.getElementById("registerName").value;
    const confirmPassword = document.getElementById("registerConfirmPassword").value;
    //create user returns the proper user json structure with null filled values
    const user = createUser({email: email, name: name, password: password})
    const validationData = validateUserDataObject(user, confirmPassword);
    if (!validationData.isValid){
        alert("INVALID REGISTRATION DATA " + validationData.message);
        return;
    }
    user.password = hashSync(user.password, salt);
    //We must pass the salt because it needs to be stored in our db
    register(user, salt);
}
const testTryLogin = (event) => {
    event.preventDefault();
    const emailValue = document.getElementById("loginEmail").value;
    getSalt(emailValue)
    .then((salt) => {
        const passwordValue = document.getElementById("loginPassword").value;
        const hashedPW = hashSync(passwordValue, salt);
        const user = createUser({email: emailValue, password: hashedPW})
        login(user);
    })
}

export function RegisterForm() {
    const handleSubmit= (e) => {
        e.preventDefault();
        testTryRegister(e);
    }
    return (
        <div>
            <h1>Register user</h1>
            <form onSubmit={e => {handleSubmit(e)}}>
                <label htmlFor="name">Name:</label>
                <input id="registerName" name='name' type="text" /><br />
                <label htmlFor="email">Email:</label>
                <input id="registerEmail" name='email' type="text" /><br />
                <label htmlFor="password">Password:</label>
                <input id="registerPassword" name='password' type="password" /><br />
                <label htmlFor="confirmPassword">Confirm Password:</label>
                <input id="registerConfirmPassword" name='confirmPassword' type="password" /><br />
                <input type="submit" value="Send Request" />
            </form>
        </div>
    )
}
export function LoginForm() {
    const handleSubmit= (e) => {
        e.preventDefault();
        testTryLogin(e);
    }
    return (
        <div>
            <h1>Login user</h1>
            <form onSubmit={e => {handleSubmit(e)}}>
                <label htmlFor="email">Email:</label>
                <input id="loginEmail" name='email' type="text" /><br />
                <label htmlFor="password">Password:</label>
                <input id="loginPassword" name='password' type="password" /><br />
                <input type="submit" value="Send Request" />
            </form>
        </div>
    )
}

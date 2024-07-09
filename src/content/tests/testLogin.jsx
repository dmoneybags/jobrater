import React, { createElement } from 'react';
import ReactDOM from 'react-dom';
import {genSaltSync, hashSync} from 'bcryptjs';
import {createUser} from '../users';

//Tests to test our methods to call the servers and the server methods themselves
//will add fakerjs eventually
//db must be cleared at the start to avoid duplicant adds
let jobData = null

fetch('./testJob.json')
    .then((response) => response.json())
    .then((json) => jobData = json);

function assert(condition, message) {
    if (!condition) {
        throw new Error(message || "Assertion failed");
    }
}

//Auth tests

//test that a proper user can register
const registerTest = () => {
    let salt = genSaltSync();
    let password = "blorgnine27#"
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
        alert("INVALID REGISTRATION DATA " + validationData.message);
        return;
    }
    user.password = hashSync(user.password, salt);
    //We must pass the salt because it needs to be stored in our db
    register(user, salt)
    .then(() => {
        console.log("Register suceeded")
        console.log("Starting mock register test for valid user");
        const userRead = getActiveUser();
        //test that active user gets set
        assert(userRead !== null && userRead !== undefined);
        assert(userRead.name === name);
        assert(userRead.email === email);
        assert(!user.password);
        console.log("USER CORRECTLY READ");
        //test that token gets properly set
        const token = getToken();
        assert(token !== null && token !== undefined);
        console.log("TOKEN READ");
    })
}
//test that a improper user can't register
const registerTestNegativeDupEmail = () => {
    let salt = genSaltSync();
    let password = "scooby-Dooby-DOO"
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
        alert("INVALID REGISTRATION DATA " + validationData.message);
        return;
    }
    user.password = hashSync(user.password, salt);
    //We must pass the salt because it needs to be stored in our db
    console.log("Starting mock register test for duplicate user");
    register(user, salt)
    .then((_) => {
        console.log("Register response receieved, test FAILED");
        assert(true);
    })
    .catch((error) => {
        console.log("Register response receieved, test PASSED");
    })
}
//test that an improper user can't
const registerTestNegativeBadData = () => {
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
        alert("INVALID REGISTRATION DATA " + validationData.message);
        console.log("PASSED TEST")
        return;
    }
    console.log("FAILED INVALID REGISTRATION DATA TEST");
    assert(false);
}
//test that a user in db can login
//test that active user and token get set
const loginTest = () => {
    const emailValue = "gloobelGOB@hotmail.com";
    getSalt(emailValue)
    .then((salt) => {
        const passwordValue = "blorgnine27#";
        const hashedPW = hashSync(passwordValue, salt);
        const user = createUser({email: emailValue, password: hashedPW})
        console.log("BEGINNING LOGIN USER TESTS");
        login(user)
        .then(() =>{
            console.log("User successfully ")
            const userRead = getActiveUser();
            //test that active user gets set
            assert(userRead !== null && userRead !== undefined);
            assert(userRead.name === name);
            assert(userRead.email === email);
            assert(!user.password);
            console.log("USER CORRECTLY READ");
            //test that token gets properly set
            const token = getToken();
            assert(token !== null && token !== undefined);
            console.log("TOKEN READ");
        })
        .catch((error) => {
            console.log("LOGIN USER TEST FAILED WITH ERROR: " + error);
        });
    })
}
//test that a user not in db can't 

//Token tests

//Test that request with good token works
const testTryAddJob = () => {
    console.log("ATTEMPTING TO ADD JOB FOR USER");
    sendMessageToAddJob(jobData)
    .then((response) => {
        console.log("SUCCESSFULLY ADDED JOB WITH RESPONSE:");
        console.log(response);
    })
    .catch((error) => {
        console.log("FAILED TO ADD USER WITH ERROR:");
        console.log(error);
        assert(false);
    })
}
//test that request with bad token doesnt work
const testTryAddJobNegative = () => {
    console.log("ATTEMPTING TO ADD JOB FOR USER WITH BAD TOKEN");
    setToken("DHGWIPGNVNWPEFI!#IRN##PI!NDSAINFASF");
    sendMessageToAddJob(jobData)
    .then((response) => {
        console.log("NEGATIVE JOB TEST FAILED POOR TOKEN WORKED WITH RESP:")
        console.log(response);
        assert(false);
    })
    .catch((error) => {
        console.log("NEGATIVE TEST PROPERLY FAILED WITH ERROR:");
        console.log(error);
    })
}
//test that request with no token doesnt work
const testTryAddJobNoToken = () => {
    console.log("ATTEMPTING TO ADD JOB FOR USER WITH BAD TOKEN");
    setToken("");
    sendMessageToAddJob(jobData)
    .then((response) => {
        console.log("NEGATIVE JOB TEST FAILED POOR TOKEN WORKED WITH RESP:")
        console.log(response);
        assert(false);
    })
    .catch((error) => {
        console.log("NEGATIVE TEST PROPERLY FAILED WITH ERROR:");
        console.log(error);
    })
}
//test that token can get user from it
const testTryDeleteUser = () => {
    console.log("ATTEMPTING TO DELETE USER");
    console.log("RELOGGING IN USER");
    const emailValue = "gloobelGOB@hotmail.com";
    getSalt(emailValue)
    .then((salt) => {
        const passwordValue = "blorgnine27";
        const hashedPW = hashSync(passwordValue, salt);
        let user = createUser({email: emailValue, password: hashedPW})
        console.log("BEGINNING LOGIN USER TESTS");
        login(user)
        .then(() =>{
            let user = getActiveUser();
            sendMessageToDeleteUser(user)
            .then((resp) => {
                console.log("SUCCESSFULLY GOT USER FROM TOKEN AND DELETED WITH RESP");
                console.log(resp);
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
const attemptToReloginUserAfterDelete = () => {
    console.log("ATTEMPTING TO LOGIN PREVIOUSLY DELETED USER");
    const emailValue = "gloobelGOB@hotmail.com";
    getSalt(emailValue)
    .then((salt) => {
        const passwordValue = "blorgnine27";
        const hashedPW = hashSync(passwordValue, salt);
        let user = createUser({email: emailValue, password: hashedPW})
        console.log("BEGINNING LOGIN USER TESTS");
        login(user)
        .then(() =>{
            console.log("FAILED TEST, USER WAS ABLE TO LOGIN");
            assert(false);
        })
        .catch((error) => {
            console.log("LOGGING IN USER TEST PASSED WITH ERROR: " + error);
        });
    })
}

//MAIN:
function runTests(){
    registerTest();
    //registerTestNegativeDupEmail();
    //registerTestNegativeBadData();
    //loginTest();
    //testTryAddJob();
    //testTryAddJobNegative();
    //testTryAddJobNoToken();
    //testTryDeleteUser();
    //attemptToReloginUserAfterDelete();
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

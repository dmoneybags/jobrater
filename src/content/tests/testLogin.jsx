import React, { createElement } from 'react';
import ReactDOM from 'react-dom';
import {genSaltSync, hashSync} from 'bcryptjs';
import {createUser} from '../users';

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

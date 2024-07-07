import React, { createElement } from 'react';
import ReactDOM from 'react-dom';

const testTryRegister = (event) => {
    event.preventDefault();
    //random data for cryptography
    //to do: key exchange or store salt in db
    var salt = bcrypt.genSaltSync(10);
    const email = document.getElementById("registerEmail").value;
    const password = bcrypt.hashSync(document.getElementById("registerPassword").value, salt);;
    const name = document.getElementById("registerName").value;
    const confirmPassword = document.getElementById("registerConfirmPassword").value;
    const user = {
        "email": email,
        "password": password,
        "name": name
    }
    const validationData = validateUserDataObject(user, confirmPassword);
    if (!validationData.isValid){
        alert("INVALID REGISTRATION DATA " + validationData.message);
        return;
    }
    register(user);
}
const testTryLogin = (event) => {
    event.preventDefault();
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    const user = {
        "email": email,
        //TO DO encrypt password
        "password": password
    }
    login(user);
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

/*
Execution flow:

SignUp.html: prompts user to sign up

\/
\/

userValidation.js: ensures data passed to sign up and login functions is valid
*/
MINIMUMPASSWORDLENGTH = 8;

//Called when a user enters their email, returns true for valid email false for invalid email
const validateEmail = (email) => {
    const regEx = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/g;
    //return true if we find a match false if not
    return regEx.test(email);
}
const getStrengthValues = (password) => {
    //return values are 
    //0: whether or not the string contains a special character
    //1: whether or not the string is over 8 characters
    //2: is there a caps
    let returnValues = [false, false, false];
    const specialCharactersPattern = /[!@#$%^&*(),.?":{}|<>]/;
    const capsCharactersPattern = /[A-Z]/;
    returnValues[0] = specialCharactersPattern.test(password);
    returnValues[1] = password.length >= MINIMUMPASSWORDLENGTH;
    returnValues[2] = capsCharactersPattern.test(capsCharactersPattern);
    return returnValues;
}
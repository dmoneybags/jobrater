/*
Execution flow:

SignUp.html: prompts user to sign up

\/
\/

userValidation.js: ensures data passed to sign up and login functions is valid

structure of userDataObject:

VERY BASIC ALPHA STRUCTURE
user {
    UserID VARCHAR(36) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255),
    Google_Id VARCHAR(255) UNIQUE,
    Name VARCHAR(255),
}

GROUND TRUTH, SQL DB and USER_COLUMNS IN database_functions.py
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
//execution flow:
//  We check the users email on the login sheet or sign up sheet immeadiately after
//  they type it to make sure they do not already have an account
//  THEREFORE, we do not need to check it here.
//returns
//  isValid: true if the data is valid
//  message: why the message is invalid
//  code: correlates to the reason why it isnt valid
//  1: invalid email
//  2: weak password
//  3: no mathc
//  0: valid
const validateUserDataObject = (userDataObject, retypedPassword) => {
    if (!validateEmail(userDataObject["email"])){
        return {
            isValid: false,
            message: "invalid email",
            code: 1
        }
    }
    if (getStrengthValues(userDataObject).includes(false)){
        return {
            isValid: false,
            message: "weak password",
            code: 2
        }
    }
    if (userDataObject["password"] !== retypedPassword){
        return {
            isValid: false,
            message: "passwords don't match",
            code: 3
        }
    }
    return {
        isValid: true,
        message: "Valid user data",
        code: 0
    }
}
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
const MINIMUMPASSWORDLENGTH: number = 8;

/**
 * validateEmail
 * 
 * Called when a user enters their email, returns true for valid email false for invalid email
 * 
 * @param {string} email - email we are attmepting to validate
 * @returns {boolean}
 */
const validateEmail = (email: string) => {
    const regEx : RegExp= /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/g;
    //return true if we find a match false if not
    return regEx.test(email);
}
/**
 * getStrengthValues
 * 
 * Tests the password on 3 tests (has special characters, length is correct, and has caps)
 * 
 * @param {string} password - the string password of the user, unhashed
 * @returns {boolean[]} result for each test as given in the order above
 */
const getStrengthValues = (password: string): boolean[]  => {
    //return values are 
    //0: whether or not the string contains a special character
    //1: whether or not the string is over 8 characters
    //2: is there a caps
    let returnValues: boolean[] = [false, false, false];
    const specialCharactersPattern: RegExp = /[!@#$%^&*(),.?":{}|<>]/;
    const capsCharactersPattern: RegExp = /[A-Z]/;
    returnValues[0] = specialCharactersPattern.test(password);
    console.log("passwordLength: " + password.length);
    returnValues[1] = password.length >= MINIMUMPASSWORDLENGTH;
    returnValues[2] = capsCharactersPattern.test(String(capsCharactersPattern));
    console.log("PASSWORD CONTAINS SPECIAL CHARACTER: " + returnValues[0] + 
        ", PASSWORD is long enough: " + returnValues[1] + 
        ", PASSWORD HAS CAPS " + returnValues[2]);
    return returnValues;
}
/**
 * validateUserJson
 * 
 * ensures that a users data is valid before registration
 * 
 * returns json descibing the validity
 * 
 * @param {Record<string, any>} userJson 
 * @param {string} retypedPassword 
 * @returns {Record<string, any>} 
 * {
 *  isValid: whether or not data is valid
 *  message: why its invalid
 *  code: code that corresponds to that invalid reason
 * }
 */
const validateUserJson = (userJson: Record<string, any>, retypedPassword: string) => {
    if (!validateEmail(userJson["email"])){
        return {
            isValid: false,
            message: "invalid email",
            code: 1
        }
    }
    if (getStrengthValues(userJson.password).includes(false)){
        return {
            isValid: false,
            message: "weak password",
            code: 2
        }
    }
    if (userJson["password"] !== retypedPassword){
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
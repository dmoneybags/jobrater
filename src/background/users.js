/*
User code needs to:
 -validation
    -evaluate whether a email from our front end code is valid
    validateEmail(email) -> Bool
    -evaluate whether a password is strong enough
    getStrengthValues(password) -> [bool] -> [containsSpecialChar, isOver8char, hasNumber]
    -compare a retype password value
    just simple equals
    -evaluate if a userObject is valid before signing up
    validateUserDataObject(userObject, retyped password) -> Promise(resolve: True, reject: reasonForInvalid)
        returns promise because we have a db call
        CALLS AFTER: all inputs are entered on the front end and we need to make sure the data is correct before
        adding to our db
        calls:
            validateEmail
            getStrengthValues
            compares passwords
            doesExist
 -API calls
    -evaluate whether email already exists in db
    doesExist(email) -> Promise(resolve: userDataObject, reject: false)
    -call to our database server to add a user on sign up
    addUserToDb(userJson) -> Promise(resolve: -> token, reject -> error)
    -call to our database server to read a user object on email flagging user exists
    readUserByEmail(userEmail) -> Promise(resolve: UserObject, reject -> None)
    -HASHED password
    -call to google to auth through gmail
        authViaGoogle(callbackURL) -> done(error, user, info) info will have whether or not its a new user
-Persistence
    -get token from server on successful login
        ENSURE ONLY AUTHENTIFICATED CALLERS CAN ACCESS
        getToken(userID) -> Promise(resolve: token, reject: error)
    -set token in local storage:
        setToken(token) -> error?
    -send token on ALL subsequent request
        two functions will be needed
        ? for can be None
        grabLocalUserToken() -> token?
    -every request will need a token
        add grabLocalUserToken to all db calls
    -get user from token
        getUserDataFromToken(token) -> Promise(resolve: userJson, reject: error)
    -set active userData wherever we choose to
        setUserData(userData) -> error?
-Authentification
    -compare password hashes
        checkPassword(givenPassword, userPassword) -> "done" object
    -send response to login user
        return of the doneObject, set active user in ?
    *OverArching function:
    attemptToLoginUser(userObject, password) -> Promse(resolve: token, reject: error)
        -CALLED AFTER: userObject is successfully grabbed from db upon email enter
        -CALLS:
            checkPassword
            handles: errors, incorrect object, promise rejections
        -IF THERE'S NO ERROR:
            jwt = getToken(userID)
            setToken(jwt)
            userData = getUserDataFromToken(jwt)
            setUserData(userData)
    attemptToSignUpUser(userObject) -> Promise(resolve: token, reject: error)
        -CALLED AFTER: user data is ensured to be a new user and fully validated
        -CALLS:
            addUserToDB
*/ 
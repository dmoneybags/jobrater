/*
Execution flow:

SignUp.html: prompts user to sign up

\/
\/

googleAuth.js
leads here if the user chooses to sign up with google
*/

//SERVER SIDE CODE

const GoogleStrategy = require('passport-google-oauth20').Strategy;

passport.use(new GoogleStrategy({
    clientSecret: process.env.GOOGLE_API_KEY,
    //placeholder url
    callbackURL: 'http://localhost:3000/auth/google/callback'
}, (token, tokenSecret, profile, done) => {
    getUserByGoogleId(profile.id)
    .then((userJson) => {
        if (userJson){
            return done(null, userJson);
        }
        const newUserArgs = {
            google_id: profile.id,
            name: profile.displayName,
            email: profile.emails[0].value,
            password: null
        };
        const user = createUser(newUserArgs);
        register(newUser, 0)
        .then(() => {
            return done(null, newUser)
        })
        .catch((error) => {
            console.log("Recieved error of " + error + " trying to add job after google auth, no user added");
            return done(error, null)
        })
    })
    .catch((error) => {
        console.log("Recieved error of " + error + " trying to read the db for google id of " + profile.id);
        const newUserArgs = {
            google_id: profile.id,
            name: profile.displayName,
            email: profile.emails[0].value,
            password: null
        };
        const user = createUser(newUserArgs);
        register(newUser, 0)
        .then(() => {
            return done(null, newUser)
        })
        .catch((error) => {
            console.log("Recieved error of " + error + " trying to add user after google auth, no user added");
            return done(error, null)
        })
    })
}));
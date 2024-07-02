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
const bcrypt = require('bcryptjs');

passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    //placeholder url
    callbackURL: 'http://localhost:3000/auth/google/callback'
}, (token, tokenSecret, profile, done) => {
    getUserByGoogleId(profile.id)
    .then((userJson) => {
        if (userJson){
            return done(null, userJson);
        }
        newUser = {
            google_id: profile.id,
            name: profile.displayName,
            email: profile.emails[0].value,
            password: null
        }
        sendMessageToAddUser(newUser)
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
        newUser = {
            google_id: profile.id,
            name: profile.displayName,
            email: profile.emails[0].value,
            password: null
        }
        sendMessageToAddUser(newUser)
        .then(() => {
            return done(null, newUser)
        })
        .catch((error) => {
            console.log("Recieved error of " + error + " trying to add job after google auth, no user added");
            return done(error, null)
        })
    })
}));
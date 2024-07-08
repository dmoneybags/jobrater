import { createUser } from "../users";
import {genSaltSync, hashSync} from 'bcryptjs';

TESTPASSWORD = "blorgnine280"

//DB MUST BE CLEARED AT THE START
const testRegisteringUser = () => {
    const salt = genSaltSync();
    const user = createUser({email: "dandemoney@gmail.com",
        password: hashSync(TESTPASSWORD, salt),
        name: "Daniel DeMoney"
    })
    register(user, salt)
    .then((message) => {
        console.log("SUCCESSFULLY ADDED USER");
        //read user
    })
    .catch(() => {
        console.log("RECIEVED AN ERROR ON REGISTERING USER!")
    })
}
const runTests = () => {
    testRegisteringUser()
}
runTests();
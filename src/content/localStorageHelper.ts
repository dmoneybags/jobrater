import { Job, JobFactory } from "./job";
import { User, UserFactory} from "./user";

export class LocalStorageHelper {
    /**
     * readJobs
     * 
     * reads jobs from localStorage 
     * @returns {Job[]} the list of jobs read from localStorage, will be empty list if none were found
     */
    static readJobs():Job[]{
        const jobsStr = localStorage.getItem("jobs");
        if (!jobsStr){
            console.warn("No jobs found in local storage");
            return [];
        }
        const jobsJson: Record<string, any>[] = JSON.parse(jobsStr);
        const jobList: Job[] = jobsJson.map((job) => JobFactory.generateFromJson(job))
        return jobList;
    }
    /**
     * saveJobs
     * 
     * saves the jobs to localStorage
     * 
     * @param {Job[]} jobs - the jobs we are saving 
     */
    static saveJobs(jobs: Job[]):void{
        const jsonJobs: Record<string, any> = jobs.map((job) => job.toJson())
        const jsonJobsStr: string = JSON.stringify(jsonJobs);
        localStorage.setItem("jobs", jsonJobsStr);
    }
    /**
     * addJob
     * 
     * adds a job to our job list in localStorage
     * 
     * @param {Job} job the job we are adding to our job list
     */
    static addJob(job: Job):void{
        const jobs: Job[] = LocalStorageHelper.readJobs();
        jobs.push(job);
        LocalStorageHelper.saveJobs(jobs);
    }
    /**
     * getActiveUser
     * 
     * grabs representation of active user from localstorage
     * 
     * @returns {User | null} User in active storage if we didnt find it, returns null
     */
    static getActiveUser = (): User | null => {
        const userJsonString : string | null = localStorage.getItem("activeUser");
        if (!userJsonString){
            console.warn("Failed to get user from localStorage, returning null");
            return null;
        }
        const userJson: Record<string, any> = JSON.parse(userJsonString);
        return UserFactory.generateFromJson(userJson);
    }
    /**
     * setToken
     * 
     * Sets the auth token in local storage
     * @param token : string, the string token recieved from the server
     */
    static setToken = (token : string): void => {
        console.log("Setting auth token to " + token);
        localStorage.setItem("authToken", token);
    }
    /** 
    getToken

    returns the users token if found, else null
    @returns {string | null} the token or null
    */
    static getToken = (): string | null => {
        const token : string | null = localStorage.getItem("authToken");
        if (!token){
            console.warn("NO TOKEN LOADED")
        }
        return token
    }
    /**
     * setActiveUser
     * 
     * Sets users data in localStorage after login/register
     * @param {User} user: the user object we are setting active user to
     * @see: TODO add user jobs to localstorage
     * @see: add expiration data to data
     */
    static setActiveUser = (user: User) => {
        console.log("SETTING ACTIVE USER TO " + JSON.stringify(user));
        localStorage.setItem("activeUser", JSON.stringify(user));
    }
}
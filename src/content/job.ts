import { LargeNumberLike } from "crypto";
import { LocationObject, LocationObjectFactory } from "./location";
import { Company, CompanyFactory } from "./company";
import { json } from "stream/consumers";

/**
 * PaymentFrequency
 * 
 * Simple enum to represent the payment frequencies in a job
 */
export class PaymentFrequency {
    str: string
    constructor(paymentStr: string){
        const paymentStrs = ["hr", "yr"];
        if (!paymentStrs.includes(paymentStr)){
            throw new Error("Invalid payment Str");
        }
        this.str = paymentStr;
    }
}
/**
 * Mode
 * 
 * Simple enum to represent the payment WFM policy in a job
 */
export class Mode {
    str: string
    constructor(modeStr: string){
        const modes = ["Remote", "Hybrid", "On-site"]
        if (!modes.includes(modeStr)){
            throw new Error("Invalid Mode Str");
        }
        this.str = modeStr
    }
}

/**
 * Job
 * 
 * Representation of all the data we hold on a job INCLUDING foreign key objects.
 * 
 * so job, the company associated with the job, and the location of the job
 * 
 * @property {string} jobId: the string job id for the job. current implementation is just the 
 * linkedin unique url slug, this may very change in the future.
 * @property {number} applicants: the number of applicants in the "# people applied" on linkedin
 * @property {string} careerStage: the careerStage of the company such as the associate, director, etc str on linkedin
 * @property {string} jobName: the name of the job
 * @property {Company} company: the company object associated with the job
 * @property {number} paymentBase: lower level amount of the payment ex "100k-120k per yr" 100k is the base
 * @property {PaymentFrequency} paymentFreq: the payment frequency of the job. It is a separate enum
 * @property {number} paymentHigh: in previous example 120k would be the paymentHigh
 * @property {string} locationStr: the string given for the location of the job on linkedin. 
 * Used with the google places api to find the jobs direct location.
 * @property {Mode} mode: the element of the mode enum that has the work from home policy of the job
 * @property {number} secondsPostedAgo: a seconds representation of the time since the job has been posted. 
 * Linkedin will say something like posted 2 weeks ago
 * @property {LocationObject} location: the location object for th job. will be null for remote jobs
 */
export class Job {
    jobId : string;
    applicants: number;
    careerStage: string | null;
    jobName: string;
    company: Company;
    paymentBase: number | null;
    paymentFreq: PaymentFrequency | null;
    paymentHigh: number | null;
    locationStr: string | null;
    mode: Mode;
    secondsPostedAgo: number;
    timeAdded: Date | null;
    location: LocationObject | null;
    constructor(jobId : string, applicants: number, careerStage: string | null, jobName: string, company: Company, paymentBase: number | null,
        paymentFreq: PaymentFrequency | null, paymentHigh: number | null, locationStr: string | null, mode: Mode, secondsPostedAgo: number, timeAdded: Date | null, location: LocationObject | null){
        this.jobId = jobId;
        this.applicants = applicants;
        this.careerStage = careerStage;
        this.jobName = jobName;
        this.company = company;
        this.paymentFreq = paymentFreq;
        this.paymentBase = paymentBase;
        this.paymentHigh = paymentHigh;
        this.locationStr = locationStr;
        this.mode = mode;
        this.secondsPostedAgo = secondsPostedAgo;
        this.timeAdded = timeAdded;
        this.location = location;
    }
    toJson() {
        return {
            jobId: this.jobId,
            applicants: this.applicants,
            careerStage: this.careerStage,
            jobName: this.jobName,
            company: this.company,
            //paymentFreq is passed below
            paymentBase: this.paymentBase,
            paymentHigh: this.paymentHigh,
            paymentFreq: this.paymentFreq?.str,
            locationStr: this.locationStr,
            //mode is passed below
            mode: this.mode.str,
            secondsPostedAgo: this.secondsPostedAgo,
            timeAdded: Math.floor((this.timeAdded ?? new Date()).getTime() / 1000),
            location: this.location
        }
    }
}
export class JobFactory {
    /** 
    * generateFromJson
    * 
    * Creates a job item from the formatted json passed by our content script
    * 
    * @param {Record<string, any>} jsonObject: the formatted json
    * 
    * @returns {Job}
    */
    static generateFromJson(jsonObject: Record<string, any>):Job{
        const jobId: string = jsonObject["jobId"];
        const applicants: number = jsonObject["applicants"];
        const careerStage: string = jsonObject["careerStage"];
        const jobName: string = jsonObject["jobName"];
        var company: Company
        try {
            company = CompanyFactory.generateFromJson(jsonObject["company"])
        } catch {TypeError} {
            company = CompanyFactory.generateEmptyCompany(jsonObject["company"]["companyName"])
        }
        const paymentFreq: PaymentFrequency | null = jsonObject["paymentFreq"] ? PaymentFrequency[jsonObject["paymentFreq"]] : null;
        const paymentBase: number | null = jsonObject["paymentBase"];
        const paymentHigh: number | null = jsonObject["paymentHigh"];
        const locationStr: string | null = jsonObject["locationStr"];
        const mode: Mode = new Mode(jsonObject["mode"]);
        const secondsPostedAgo: number = jsonObject["secondsPostedAgo"];
        //
        const timeAdded: Date = new Date(Number(jsonObject["timeAdded"] * 1000));
        var location: LocationObject | null;
        try {
            location = LocationObjectFactory.generateLocationFromJson(jsonObject["location"]);
        } catch {TypeError} {
            location = null;
        }
        return new Job(jobId, applicants, careerStage, jobName, company, paymentBase, paymentFreq, paymentHigh, 
            locationStr, mode, secondsPostedAgo, timeAdded, location
        )
    }
}
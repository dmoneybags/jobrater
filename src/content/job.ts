import { LargeNumberLike } from "crypto";
import { LocationObject, LocationObjectFactory } from "./location";
import { Company, CompanyFactory } from "./company";
import { json } from "stream/consumers";

enum PaymentFrequency {
    hr = 1,
    yr,
}
enum Mode {
    remote = 1,
    hybrid,
    onsite,
}

class Job {
    jobId : string;
    applicants: number;
    careerStage: string;
    jobName: string;
    company: Company;
    paymentBase: number | null;
    paymentFreq: PaymentFrequency | null;
    paymentHigh: number | null;
    locationStr: string | null;
    mode: Mode;
    secondsPostedAgo: number;
    timeAdded: Date;
    location: LocationObject | null;
    constructor(jobId : string, applicants: number, careerStage: string, jobName: string, company: Company, paymentBase: number | null,
        paymentFreq: PaymentFrequency | null, paymentHigh: number | null, locationStr: string | null, mode: Mode, secondsPostedAgo: number, timeAdded: Date, location: LocationObject | null){
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
    static strToPaymentFreq(paymentFreqStr: string): PaymentFrequency {
        if (paymentFreqStr === "hr"){
            return PaymentFrequency.hr
        } else if (paymentFreqStr === "yr"){
            return PaymentFrequency.yr
        }
        throw new TypeError("Invalid paymentFreqStr Passed " + paymentFreqStr);
    }
    static strToMode(modeStr: string): Mode {
        const modeStrs: string[] = ["Remote", "Hybrid", "On-site"]
        return Mode[modeStrs.find((element) => element === modeStr) ?? "Remote"];
    }
    toJson() {
        return {
            jobId: this.jobId,
            applicants: this.applicants,
            careerStage: this.careerStage,
            jobName: this.jobName,
            company: JSON.stringify(this.company),
            //paymentFreq is passed below
            paymentBase: this.paymentBase,
            paymentHigh: this.paymentHigh,
            locationStr: this.locationStr,
            //mode is passed below
            secondsPostedAgo: this.secondsPostedAgo,
            timeAdded: Math.floor(this.timeAdded.getTime() / 1000),
            location: JSON.stringify(this.location)
        }
    }
}
class JobFactory {
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
        const paymentFreq: PaymentFrequency | null = jsonObject["paymentFreq"] ? Job.strToPaymentFreq(jsonObject["paymentFreq"]) : null;
        const paymentBase: number | null = jsonObject["paymentBase"];
        const paymentHigh: number | null = jsonObject["paymentHigh"];
        const locationStr: string | null = jsonObject["locationStr"];
        const mode: Mode = Job.strToMode(jsonObject["mode"]);
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
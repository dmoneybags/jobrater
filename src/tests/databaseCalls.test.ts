//Tests for the file databaseCalls
import { execSync } from 'child_process';
import { DatabaseCalls } from "../content/databaseCalls";
import { Company, CompanyFactory } from '../content/company';
import { Job, JobFactory, Mode, PaymentFrequency } from '../content/job';
import { User } from '../content/user';
import { register } from '../content/auth';
import { genSaltSync } from 'bcryptjs-react';

describe("DatabaseCalls.ts file tests", () => {
    beforeAll(() => {
        // clear our db
        execSync('buildjobrater', { stdio: 'inherit' });
    });
    it("tests that we properly get info back when company doesn't exist", () => {
        return expect(DatabaseCalls.checkIfCompanyExists("Initech")).resolves.toEqual(false);
    })
    it("tests that we cannot add a job without a token", ()=> {
        const companyJson : Record<string, any> = {
            companyName: "Initech",
            businessOutlookRating: 4.2,
            careerOpportunitesRating: 3.4,
            ceoRating: 3.7,
            compensationAndBenefitsRating: 4.1,
            cultureAndValuesRating: 4.0,
            diversityAndInclusionRating: 4.9,
            seniorManagementRating: 1.3,
            workLifeBalanceRating: 4.8,
            overallRating: 2.1
        };
        const company: Company = CompanyFactory.generateFromJson(companyJson);
        const job: Job = new Job("1252154223", 49, "Director", "Software Engineer", company, 123000, new PaymentFrequency("yr"),
                                141000, "Remote", new Mode("Remote"), 10000, null, null
        );
        return expect(DatabaseCalls.sendMessageToAddJob(job)).rejects.toEqual("401");
    })
    it("Tests that we can add a job with a token", async () => {

        const mockUser: User = new User("_", "dandemoney@gmail.com", null, "Daniel", "DeMoney", null);

        await register(mockUser, "Xdfgh1012#", "Xdfgh1012#", genSaltSync());

        const companyJson: Record<string, any> = {
            companyName: "Initech",
            businessOutlookRating: 4.2,
            careerOpportunitesRating: 3.4,
            ceoRating: 3.7,
            compensationAndBenefitsRating: 4.1,
            cultureAndValuesRating: 4.0,
            diversityAndInclusionRating: 4.9,
            seniorManagementRating: 1.3,
            workLifeBalanceRating: 4.8,
            overallRating: 2.1
        };

        const company: Company = CompanyFactory.generateFromJson(companyJson);
        const job: Job = new Job(
            "1252154223", 
            49, 
            "Director", 
            "Software Engineer", 
            company, 
            123000, 
            new PaymentFrequency("yr"),
            141000, 
            "Remote", 
            new Mode("Remote"), 
            10000, 
            null, 
            null
        );
        await expect(DatabaseCalls.sendMessageToAddJob(job)).resolves.not.toThrow();
    })
    it("tests that we can add jobs with null values", ()=>{

    })
    it("tests that we can properly read the job back with foriegn keys after a read", ()=>{

    })
    it("tests that we cannot add a duplicate job", ()=>{

    })
    it("tests that the company is added into the database after adding a job", ()=>{

    })
    it("tests that we can properly load userdata after a login", ()=>{
        
    })
    it("tests that we can properly load userdata after a register", ()=>{
        console.log("This rebuilds the app for a clean register and resets localStorage");
    })
    it("tests that we get a 401 without a valid token", ()=> {
        console.log("This clears the token and would trigger a reauth");
    })
    it("tests that we can delete a user", ()=> {
        
    })
})
import { User } from "../../content/user";
import { Company, CompanyFactory } from "../../content/company";
import { LocationObject } from "../../content/location"
import { PaymentFrequency, Mode, Job } from "../../content/job";

//Mock file for objects used in our tests
export class MockObjects {
    static dandemoney_user: User = new User("_", "dandemoney@gmail.com", null, "Daniel", "DeMoney", null);
    static apple_with_data_company : Company = CompanyFactory.generateFromJson({
        companyName: "Apple",
        businessOutlookRating: 4.2,
        careerOpportunitiesRating: 3.4,
        ceoRating: 3.7,
        compensationAndBenefitsRating: 4.1,
        cultureAndValuesRating: 4.0,
        diversityAndInclusionRating: 4.9,
        seniorManagementRating: 1.3,
        workLifeBalanceRating: 4.8,
        overallRating: 2.1
    });
    static initech_with_data_company : Company = CompanyFactory.generateFromJson({
        companyName: "Initech",
        businessOutlookRating: 4.2,
        careerOpportunitiesRating: 3.4,
        ceoRating: 3.7,
        compensationAndBenefitsRating: 4.1,
        cultureAndValuesRating: 4.0,
        diversityAndInclusionRating: 4.9,
        seniorManagementRating: 1.3,
        workLifeBalanceRating: 4.8,
        overallRating: 2.1
    });
    static initech_software_engineer_job : Job = new Job(
        "1252154224", 
        49, 
        "Director", 
        "Software Engineer", 
        MockObjects.initech_with_data_company, 
        123000, 
        new PaymentFrequency("yr"),
        141000, 
        "Remote", 
        new Mode("Remote"), 
        10000, 
        null, 
        null
    );
    static apple_software_engineer_job: Job = new Job(
        "1252154223", 
        49, 
        null, 
        "Software Engineer", 
        MockObjects.apple_with_data_company, 
        null, 
        null,
        null, 
        null, 
        new Mode("Remote"), 
        10000, 
        null, 
        null
    );
    static apple_with_null_values_company: Company = CompanyFactory.generateFromJson({
        companyName: "Apple",
        businessOutlookRating: 0,
        careerOpportunitiesRating: 0,
        ceoRating: 0,
        compensationAndBenefitsRating: 0,
        cultureAndValuesRating: 0,
        diversityAndInclusionRating: 0,
        seniorManagementRating: 0,
        workLifeBalanceRating: 0,
        overallRating: 0
    });
    static apple_null_values_big_hoss_job: Job = new Job(
        "1252154290", 
        49, 
        "Associate", 
        "Big Hoss", 
        MockObjects.apple_with_null_values_company, 
        121000, 
        new PaymentFrequency("yr"),
        140000, 
        "Cupertino, CA", 
        new Mode("Hybrid"), 
        10000, 
        null, 
        null
    )
    static apple_location: LocationObject = new LocationObject(
        "One Apple Park Way", "Cupertino", "95014", "CA", 37.334606, -122.009102
    )
}

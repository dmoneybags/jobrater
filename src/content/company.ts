import { json } from "stream/consumers";

export class Company {
    companyName : string;
    businessOutlookRating: number;
    careerOpportunitesRating: number;
    ceoRating: number;
    compensationAndBenefitsRating: number;
    cultureAndValuesRating: number;
    diversityAndInclusionRating: number;
    seniorManagementRating: number;
    workLifeBalanceRating: number;
    overallRating: number;
    constructor(companyName: string, businessOutlookRating: number, careerOpportunitesRating: number, ceoRating: number,
        compensationAndBenefitsRating: number, cultureAndValuesRating: number, diversityAndInclusionRating: number,
        seniorManagementRating: number, workLifeBalanceRating: number, overallRating: number
    ){
        this.companyName = companyName;
        this.businessOutlookRating = businessOutlookRating;
        this.careerOpportunitesRating = careerOpportunitesRating;
        this.ceoRating = ceoRating;
        this.compensationAndBenefitsRating = compensationAndBenefitsRating;
        this.cultureAndValuesRating = cultureAndValuesRating;
        this.diversityAndInclusionRating = diversityAndInclusionRating;
        this.seniorManagementRating = seniorManagementRating;
        this.workLifeBalanceRating = workLifeBalanceRating;
        //Kind of just a check that company data is not empty
        if (typeof overallRating !== 'number') {throw new TypeError("overallRating must be number");}
        this.overallRating = overallRating;
    }
}

export class CompanyFactory {
    static generateFromJson(json_object: Record<string, any>): Company{
        if (typeof json_object !== "object"){throw new TypeError("type of " + String(typeof json_object) + " is invalid json");}
        return new Company(json_object["companyName"], json_object["businessOutlookRating"], json_object["careerOpportunitesRating"],
            json_object["ceoRating"], json_object["compensationAndBenefitsRating"], json_object["cultureAndValuesRating"], json_object["diversityAndInclusionRating"],
            json_object["seniorManagementRating"], json_object["workLifeBalanceRating"], json_object["overallRating"]
        )
    }
    static generateEmptyCompany(companyName: string): Company{
        return new Company(companyName,0,0,0,0,0,0,0,0,0)
    }
}
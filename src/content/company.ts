import { json } from "stream/consumers";
export class Company {
    companyName : string;
    businessOutlookRating: number;
    careerOpportunitiesRating: number;
    ceoRating: number;
    compensationAndBenefitsRating: number;
    cultureAndValuesRating: number;
    diversityAndInclusionRating: number;
    seniorManagementRating: number;
    workLifeBalanceRating: number;
    overallRating: number;
    /**
     * company
     * 
     * Representation of a company within our app. For now mainly holds data scraper from glassdoor
     * 
     * @param {string} companyName
     * @param {number} businessOutlookRating 
     * @param {number} careerOpportunitiesRating 
     * @param {number} ceoRating 
     * @param {number} compensationAndBenefitsRating 
     * @param {number} cultureAndValuesRating 
     * @param {number} diversityAndInclusionRating 
     * @param {number} seniorManagementRating 
     * @param {number} workLifeBalanceRating 
     * @param {number} overallRating 
     */
    constructor(companyName: string, businessOutlookRating: number, careerOpportunitiesRating: number, ceoRating: number,
        compensationAndBenefitsRating: number, cultureAndValuesRating: number, diversityAndInclusionRating: number,
        seniorManagementRating: number, workLifeBalanceRating: number, overallRating: number
    ){
        this.companyName = companyName;
        this.businessOutlookRating = businessOutlookRating;
        this.careerOpportunitiesRating = careerOpportunitiesRating;
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
    /**
     * generateFromJson
     * 
     * generates a company object from a complete json representation of a company
     * 
     * @param {Record<string, any>} json_object: dictionary where key corresponds to the property of the 
     * company object and value the rating
     * @returns {Company} 
     */
    static generateFromJson(json_object: Record<string, any>): Company{
        return new Company(
            json_object["companyName"], 
            Number(json_object["businessOutlookRating"]), 
            Number(json_object["careerOpportunitiesRating"]),
            Number(json_object["ceoRating"]), 
            Number(json_object["compensationAndBenefitsRating"]), 
            Number(json_object["cultureAndValuesRating"]), 
            Number(json_object["diversityAndInclusionRating"]),
            Number(json_object["seniorManagementRating"]), 
            Number(json_object["workLifeBalanceRating"]), 
            Number(json_object["overallRating"])
        )
    }
    /**
     * generateEmptyCompany
     * 
     * Generates an empty placeholder company
     * 
     * @param {string} companyName 
     * @returns {Company}
     */
    static generateEmptyCompany(companyName: string): Company{
        return new Company(companyName,0,0,0,0,0,0,0,0,0)
    }
}
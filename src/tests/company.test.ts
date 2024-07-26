//Tests for the file Company.ts
import { Company, CompanyFactory } from "../content/company"
describe("Auth.ts file tests", () => {
    it("tests that companies can properly load values", () => {
        const companyJson : Record<string, any> = {
            companyName: "Apple",
            businessOutlookRating: 4.2,
            careerOpportunitesRating: 3.4,
            ceoRating: 3.7,
            compensationAndBenefitsRating: 4.1,
            cultureAndValuesRating: 4.0,
            diversityAndInclusionRating: 4.9,
            seniorManagementRating: 1.3,
            workLifeBalanceRating: 4.8,
            overallRating: 2.1
        }
        const company : Company = CompanyFactory.generateFromJson(companyJson);
        const companyStr : string = JSON.stringify(company);
        const companyJson2 : Record<string, any> = JSON.parse(companyStr);
        expect(companyJson2).toEqual(companyJson);
    })
})

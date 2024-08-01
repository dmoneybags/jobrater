//Tests for the file Company.ts
import { Company, CompanyFactory } from "../content/company"
import { MockObjects } from "./__mocks__/objects";
describe("Company.ts file tests", () => {
    it("tests that companies can properly load values", () => {
        const company : Company = MockObjects.apple_with_data_company
        const companyStr : string = JSON.stringify(company);
        const companyJson2 : Record<string, any> = JSON.parse(companyStr);
        expect(companyJson2).toEqual(company);
    })
})

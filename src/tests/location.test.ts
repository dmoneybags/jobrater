//Tests for the file job.ts
import { LocationObject } from "../content/location"
import { MockObjects } from "./mocks/objects";
describe("Job.ts file tests", () => {
    it("tests that companies can properly load values", () => {
        const location : LocationObject = MockObjects.apple_location
        const locationStr : string = JSON.stringify(location);
        const locationJson : Record<string, any> = JSON.parse(locationStr);
        expect(locationJson).toEqual(location);
    })
})

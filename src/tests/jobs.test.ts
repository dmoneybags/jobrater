//Tests for the file job.ts
import { Job, JobFactory } from "../content/job"
import { MockObjects } from "./mocks/objects";
describe("Job.ts file tests", () => {
    it("tests that companies can properly load values", () => {
        const job : Job = MockObjects.apple_software_engineer_job
        const jobStr : string = JSON.stringify(job);
        const jobJson : Record<string, any> = JSON.parse(jobStr);
        expect(jobJson).toEqual(job);
    })
})

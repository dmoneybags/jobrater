import { Resume, ResumeFactory } from "../content/resume";
import { promisify } from 'util';
import * as fs from 'fs';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
describe("Resume.ts file tests", () => {
    it("Tests that resumes can load and dump files consistently", async ()=>{
        const fileBuffer : Buffer = await readFile("./src/tests/mocks/resume.pdf");
        const file : File = new File([fileBuffer], "resume.pdf", {
            type: 'application/pdf'
        })
        const resume : Resume = await ResumeFactory.generateFromFile(file);
        await writeFile("./src/tests/mocks/redumpedResume.pdf", resume.fileContent);
        const rereadFileBuffer : Buffer = await readFile("./src/tests/mocks/redumpedResume.pdf");
        expect(rereadFileBuffer).toEqual(fileBuffer);
    })
    it("Tests that resumes can dump and be loaded to json consistently", async () =>{
        const fileBuffer : Buffer = await readFile("./src/tests/mocks/resume.pdf");
        const file : File = new File([fileBuffer], "resume.pdf", {
            type: 'application/pdf'
        })
        const resume : Resume = await ResumeFactory.generateFromFile(file);
        const resumeJson : Record<string, any> = resume.toJson();
        const rereadResume : Resume = ResumeFactory.generateFromJson(resumeJson);
        expect(resume).toEqual(rereadResume);
    })
})
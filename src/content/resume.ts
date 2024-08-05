export class Resume {
    /**
     * Resume
     * 
     * Representation of a resume within the extension.
     * 
     * @property {Number} id: Id in the sql database
     * @property {String} userId: UserId the user id of the user connected to the resume
     * @property {String} fileName: the fileName of the resume
     * @property {Uint8Array} fileContent: the content of the resume file
     * @property {String} fileText: the text of the resume
     * @property {Date} uploadDate: the date the resume was uploaded
     */
    id : Number | null;
    userId : String | null;
    fileName : String;
    fileType : String;
    fileContent : Uint8Array;
    fileText : String | null;
    uploadDate : Date | null;
    constructor(id: Number | null, userId : String | null, fileName : String, fileType : String, fileContent: Uint8Array,
        fileText : String | null, uploadDate : Date | null
    ){
        this.id = id;
        this.userId = userId;
        this.fileName = fileName;
        this.fileType = fileType;
        this.fileContent = fileContent;
        this.fileText = fileText;
        this.uploadDate = uploadDate;
    }
    toJson() {
        return {
            id: this.id,
            userId: this.userId,
            fileName: this.fileName,
            fileType: this.fileType,
            fileContent: Array.from(this.fileContent),
            fileText: this.fileText,
            uploadDate: this.uploadDate
        }
    }
}
export class ResumeFactory {
    static async fileToUint8Array(file: File): Promise<Uint8Array> {
        return new Promise<Uint8Array>((resolve, reject) => {
            const reader = new FileReader();
    
            reader.onload = () => {
                if (reader.result instanceof ArrayBuffer) {
                    resolve(new Uint8Array(reader.result));
                } else {
                    reject(new Error("Error reading file as ArrayBuffer"));
                }
            };
    
            reader.onerror = () => {
                reject(new Error("Error reading file"));
            };
    
            reader.readAsArrayBuffer(file);
        });
    }
    /** 
    * generateFromJson
    * 
    * Creates a resume item from the formatted json passed by our backend or loaded from the file
    * 
    * @param {Record<string, any>} jsonObject: the formatted json
    * 
    * @returns {Resume}
    */
    static generateFromJson(jsonObject: Record<string, any>):Resume{
        console.log("Generating Resume with json of");
        console.log(jsonObject);
        const id = jsonObject["id"];
        const userId = jsonObject["userId"];
        const fileName = jsonObject["fileName"];
        const fileType = jsonObject["fileType"];
        const fileContent = new Uint8Array(jsonObject["fileContent"]);
        const fileText = jsonObject["fileText"];
        const uploadDate = new Date(Number(jsonObject["uploadDate"] * 1000));
        return new Resume(id, userId, fileName, fileType, fileContent, fileText, uploadDate);
    }
    /**
     * generateFromFile
     * 
     * Creates a partially filled resume object from the file a user uploads
     * 
     * Supported formats: [.docx, .pdf]
     * 
     * Does not fill in file text, id, or userId that is done on the backend.
     * 
     * @param {File} file, the file the user uploads
     * 
     * @returns {Resume} resume object
     */
    static async generateFromFile(file: File):Promise<Resume> {
        const fileName: String = file.name;
        const fileType: String | undefined = file.name.split('.').pop()?.toLowerCase();
        if (fileType === undefined){
            throw new Error("Invalid file")
        }
        let fileContent: Uint8Array
        try {
            fileContent = await ResumeFactory.fileToUint8Array(file);
        } catch (error) {
            console.log("Recieved error when reading file");
            console.log(error)
            throw new error("Invalid file");
        }
        return new Resume(null, null, fileName, fileType, fileContent, null, null)
    }
}
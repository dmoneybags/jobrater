from datetime import datetime
from typing import Dict
from mysql.connector.types import RowItemType
import zlib

class Resume:
    '''
    Resume

    Object to represent the resumes users upload.

    id: auto-incremented id of the resume in the db
    user_id: uuid of user the resume is connected to
    file_name: name of the uploaded resume file
    file_type: type of file uploaded (extension, .docx for word)
    file_content: bytes, content of the resume (not a readable str)
    file_text: str, readable text of the resume
    upload_date: datetime of the upload
    '''
    def __init__(self, id: int, user_id: str, file_name: str, file_type: str, file_content: bytes, file_text: str, upload_date: datetime) -> None:
        self.id = id
        self.user_id = user_id
        self.file_name = file_name
        self.file_type = file_type
        self.file_content = file_content
        self.file_text = file_text
        self.upload_date = upload_date
    '''
    compress

    quick alogirithm for str to bytes compression, used for the text of the resume

    We just use the zlib base compress decompress algos for the resume content, (raw bytes of file)

    resume_str: text of resume

    returns:

    bytes: compressed text of resume
    '''
    def compress(resume_str: str) -> bytes:
        resume_bytes: bytes = resume_str.encode("utf-8")
        compressed_resume: bytes = zlib.compress(resume_bytes)
        return compressed_resume
    '''
    decompress

    reverse alogirthm for the above function to decompress our compressed resume text.

    compressed_resume: the compressed version of the resumes text

    retutns:

    uncompressed resume
    '''
    def decompress(compressed_resume: bytes) -> str:
        decompressed_bytes: bytes = zlib.decompress(compressed_resume)
        decompressed_resume: str = decompressed_bytes.decode("utf-8")
        return decompressed_resume
    '''
    create_with_sql_row

    creates a resume from a sql row

    sql_query_row: result of cursor.fectchone

    returns:

    resume
    '''
    @classmethod
    def create_with_sql_row(cls, sql_query_row: (Dict[str, RowItemType])) -> 'Resume':
        print("CREATING RESUME WITH SQL ROW OF: ")
        print(sql_query_row)
        id: int = sql_query_row["Id"]
        user_id: str = sql_query_row["UserId"]
        file_name: str = sql_query_row["FileName"]
        file_type: str = sql_query_row["FileType"]
        file_content: bytes = zlib.decompress(sql_query_row["FileContent"])
        file_text: str = Resume.decompress(sql_query_row["FileText"])
        upload_date: str = sql_query_row["UploadDate"]
        return cls(id, user_id, file_name, file_type, file_content, file_text, upload_date)
    '''
    create_with_json

    creates a resume based off the json object sent from client

    json:

    json object sent from client

    returns:

    resume
    '''
    @classmethod
    def create_with_json(cls, json: Dict) -> 'Resume':
        print("CREATING RESUME WITH JSON OF: ")
        print(json)
        try:
            id: int = json["id"]
        except KeyError:
            id: int = None
        user_id: str = json["userId"]
        file_name: str = json["fileName"]
        file_type: str = json["fileType"]
        file_content: bytes = json["fileContent"].encode("utf-8")
        file_text: str = json["fileText"]
        upload_date: str = json["uploadDate"]
        return cls(id, user_id, file_name, file_type, file_content, file_text, upload_date)
    '''
    to_json

    dumps a resume to json to be sent back to the client

    returns:

    json
    '''
    def to_json(self) -> Dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "fileName": self.file_name,
            "fileType": self.file_type,
            "fileContent": self.file_content.decode("utf-8"),
            "fileText": self.file_text,
            "uploadDate": self.upload_date
        }
    '''
    to_sql_friendly_json

    dumps a resume to json to be added to db, compresses necessary data

    returns:

    json
    '''
    def to_sql_friendly_json(self) -> Dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "fileName": self.file_name,
            "fileType": self.file_type,
            "fileContent": zlib.compress(self.file_content),
            "fileText": Resume.compress(self.file_text),
            "uploadDate": self.upload_date
        }
from database_functions import DatabaseFunctions
from typing import Dict
from uuid import UUID
from resume import Resume
from mysql.connector.cursor import MySQLCursor
from mysql.connector.types import RowType, RowItemType

class ResumeTable:
    '''
    __get_add_resume_query

    Holds query to add resume
    '''
    def __get_add_resume_query() -> str:
        return """
            INSERT INTO Resumes (UserId, FileName, FileType, FileContent, FileText) VALUES (%s, %s, %s, %s, %s)
        """
    '''
    __get_delete_resume_query

    Holds query to delete resume
    '''
    def __get_delete_resume_query() -> str:
        return """
            DELETE FROM Resumes WHERE Id = %s
        """
    '''
    __get_read_resumes_query

    query to get all a users resumes
    '''
    def __get_read_resumes_query() -> str:
        return """
            SELECT * FROM RESUMES WHERE UserId = %s
        """
    def __get_read_resume_by_id() -> str:
        return """
            SELECT * FROM RESUMES WHERE Id = %s
        """
    '''
    add_resume

    adds a resume to the db

    user_id: uuid of the user
    resume: Resume object we are adding
    '''
    def add_resume(user_id: UUID | str, resume: Resume) -> int:
        user_id : str = str(user_id)
        print("ADDING RESUME WITH USER ID " + user_id + " AND FILENAME OF " + resume.file_name)
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = ResumeTable.__get_add_resume_query()
        resume_json: Dict = resume.to_sql_friendly_json()
        resume_values: list = [
            user_id,
            resume_json["fileName"],
            resume_json["fileType"],
            resume_json["fileContent"],
            resume_json["fileText"]
            ]
        try:
            cursor.execute(query, resume_values)
        except Exception as e:
            print("RECIEVED ERROR WHEN ATTEMPTING TO ADD RESUME")
            print(e)
            cursor.close()
            raise e
        print("RESUME SUCCESSFULLY ADDED")
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        resume_json = resume.to_json()
        return resume_json
    '''
    delete_resume

    deletes a resume from our db

    resume_id: id of the resume we are deleting
    '''
    def delete_resume(resume_id: int) -> int:
        DatabaseFunctions.MYDB.reconnect()
        cursor : MySQLCursor = DatabaseFunctions.MYDB.cursor()
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query : str = ResumeTable.__get_delete_resume_query()
        cursor.execute(query, (resume_id,))
        print("RESUME SUCCESSFULLY DELETED")
        DatabaseFunctions.MYDB.commit()
        cursor.close()
        return 0
    '''
    read_user_resumes

    returns all resumes assoiciated with a user

    user_id: uuid or str uuid of user

    returns: list of resumes 
    '''
    def read_user_resumes(user_id: UUID | str) -> list[Resume]:
        DatabaseFunctions.MYDB.reconnect()
        cursor: MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        user_id : str = str(user_id)
        #Switch to our jobDb
        cursor.execute("USE JOBDB")
        query: str = ResumeTable.__get_read_resumes_query()
        cursor.execute(query, (user_id,))
        results: list[Dict[str, RowItemType]] = cursor.fetchall()
        results_list : list[Resume] = [Resume.create_with_sql_row(row) for row in results]
        cursor.close()
        return results_list
    '''
    read_resume_by_id

    reads resume by it's specific id

    resume_id: the id of the resume we are reading

    returns:

    resume we read
    '''
    def read_resume_by_id(resume_id: int) -> Resume:
        DatabaseFunctions.MYDB.reconnect()
        cursor: MySQLCursor = DatabaseFunctions.MYDB.cursor(dictionary=True)
        cursor.execute("USE JOBDB")
        query: str = ResumeTable.__get_read_resume_by_id()
        cursor.execute(query, (resume_id,))
        result: Dict[str, RowItemType] = cursor.fetchone()
        cursor.close()
        return Resume.create_with_sql_row(result)
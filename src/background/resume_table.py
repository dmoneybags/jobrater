from database_functions import DatabaseFunctions

class ResumeTable:
    '''
    __get_job_add_query

    gets string query to add a job

    args:
        job_json: dictionary returned from job.to_json() (or sql friendly json)
    returns:
        the query str with %s for injection
    '''
    def __get_add_job_query(job_json : Dict) -> str:
        cols : list[str] = list(job_json.keys())
        col_str : str = ", ".join(cols)
        #Creates a comma separated of %s characters for string replacement when we run the 
        #query
        vals : str = ", ".join(["%s"] * len(cols))
        return f"INSERT INTO Job ({col_str}) VALUES ({vals})"
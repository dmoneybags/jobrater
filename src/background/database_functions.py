'''
TO DO: 
*CRUD methods for company CHECK
*change our query for adding the job to be created programatically with a
    "Get job values" function and then a "generate job query" function
    All our querys should be generated this way CHECK
*Change the glassdoor calls to check if the company is already in our db CHECK

'''

'''
Execution flow:

Background.js

Listens for: a tab change event fired when the current tabs url changes
Executes: scrapes the jobId from the url
Sends: a message to the contentScript that we recieved a new job

ContentScript.js
Listens for: the new job event from background.js
Executes the scraping of the linkedin and glassdoor
Calls:

database_server.py
Listens for: requests sent on PORT 5001
Executes the database functions to CRUD jobs
Through routines in

database_functions.py

TO DO:

make sure that when we check if the company exists all the values arent null
'''
#TO DO, we should not just leave cursor open

import mysql.connector
import json
import os
import uuid
from decimal import Decimal

class DatabaseFunctions:
    #Right now we'll connect to our localhost
    HOST = "localhost"
    MYSQLUSER = "root"
    #Grab our sql password from our .zshenv file
    MYSQLPASSWORD = os.getenv("SQLPASSWORD")
    MYDB = mysql.connector.connect(
        host=HOST,
        user=MYSQLUSER,
        password=MYSQLPASSWORD
    )
    
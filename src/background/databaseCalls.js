/*
Execution flow:

ContentScript:
Scrapes page for current job
\/
\/
databaseCalls
Is called to validate if the company data already exists in our db 
is called to add company/job to db

SignUp.html
\/
\/
databaseCalls
is called to validate if a user already exists 
returns tokens
adds new users to db
*/
DROP DATABASE IF EXISTS JOBDB;
CREATE DATABASE JOBDB;
USE JOBDB;

CREATE TABLE User (
    UserId VARCHAR(36) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255),
    Google_Id VARCHAR(255) UNIQUE,
    Name VARCHAR(255),
    Location VARCHAR(255),
    Salt VARCHAR(50) NOT NULL,
CONSTRAINT User_PK PRIMARY KEY (UserID)
);
CREATE TABLE KeywordList
(
    KeywordID VARCHAR(36) NOT NULL,
    Keyword1 VARCHAR(15),
    Keyword2 VARCHAR(15),
    Keyword3 VARCHAR(15),
    Keyword4 VARCHAR(15),
    Keyword5 VARCHAR(15),
    Keyword6 VARCHAR(15),
    Keyword7 VARCHAR(15),
    Keyword8 VARCHAR(15),
    Keyword9 VARCHAR(15),
    Keyword10 VARCHAR(15),
CONSTRAINT Keyword_PK PRIMARY KEY (KeywordID)
);
CREATE TABLE Company
(
    Company VARCHAR(50) NOT NULL UNIQUE,
    BusinessOutlookRating DECIMAL(3, 2),
    CareerOpportunitiesRating DECIMAL(2, 1),
    CeoRating DECIMAL(3, 2),
    CompensationAndBenefitsRating DECIMAL(2, 1),
    CultureAndValuesRating DECIMAL(2, 1),
    DiversityAndInclusionRating DECIMAL(2, 1),
    SeniorManagementRating DECIMAL(2, 1),
    WorkLifeBalanceRating DECIMAL(2, 1),
    OverallRating DECIMAL(2, 1),
    -- timestamp added to keep our data current, if data is older than lets say a month
    -- we regrab it
    TimeAdded timestamp default current_timestamp not null,
CONSTRAINT Company_PK PRIMARY KEY (Company)
);
CREATE TABLE Job
(
    JobId VARCHAR(10) NOT NULL,
    Applicants TINYINT,
    CareerStage VARCHAR(20),
    Job VARCHAR(100),
    Company VARCHAR(50) NOT NULL,
    -- uuid to keywords, one to many
    PaymentBase DECIMAL(9, 2),
    PaymentFreq VARCHAR(8),
    PaymentHigh DECIMAL(9, 2),
    KeywordID VARCHAR(36),
    LocationStr VARCHAR(50),
    Mode VARCHAR(15),
    SecondsPostedAgo DECIMAL(7, 0),
    LocationViaGoogleMaps VARCHAR(70),
    TimeAdded timestamp default current_timestamp not null,
CONSTRAINT Job_PK PRIMARY KEY (JobId),
CONSTRAINT Job_foreign_key_company FOREIGN KEY (Company) REFERENCES Company(Company),
CONSTRAINT Job_foreign_key_keywords FOREIGN KEY (KeywordID) REFERENCES KeywordList(KeywordID)
ON DELETE CASCADE
);
CREATE TABLE UserJob
(
    -- Hash of job ID and user ID, ensures both arent already in db
    UserJobId VARCHAR(36) NOT NULL UNIQUE,
    JobId VARCHAR(10) NOT NULL,
    UserId VARCHAR(36) NOT NULL,
CONSTRAINT UserJob_PK PRIMARY KEY (UserJobId),
CONSTRAINT UserJob_FK1 FOREIGN KEY (JobId) REFERENCES Job(JobId) ON DELETE CASCADE,
CONSTRAINT UserJob_FK2 FOREIGN KEY (UserId) REFERENCES User(UserId) ON DELETE CASCADE
);
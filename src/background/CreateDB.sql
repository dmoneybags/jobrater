DROP DATABASE IF EXISTS JOBDB;
CREATE DATABASE JOBDB;
USE JOBDB;

CREATE TABLE User (
    UserId VARCHAR(36) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    -- if user auths with google we dont store password
    Password VARCHAR(255),
    GoogleId VARCHAR(255) UNIQUE,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Salt VARCHAR(50),
CONSTRAINT User_PK PRIMARY KEY (UserId)
);
CREATE TABLE Company
(
    CompanyName VARCHAR(50) NOT NULL UNIQUE,
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
CONSTRAINT Company_PK PRIMARY KEY (CompanyName)
);
CREATE TABLE Job
(
    JobId VARCHAR(10) NOT NULL,
    Applicants TINYINT,
    CareerStage VARCHAR(20),
    Job VARCHAR(100),
    Company VARCHAR(50) NOT NULL,
    Description LONGBLOB,
    -- uuid to keywords, one to many
    PaymentBase DECIMAL(9, 2),
    PaymentFreq VARCHAR(8),
    PaymentHigh DECIMAL(9, 2),
    LocationStr VARCHAR(50),
    Mode VARCHAR(15),
    SecondsPostedAgo INT(11) UNSIGNED,
    TimeAdded timestamp default current_timestamp not null,
CONSTRAINT Job_PK PRIMARY KEY (JobId),
CONSTRAINT Job_foreign_key_company FOREIGN KEY (Company) REFERENCES Company(CompanyName) ON DELETE CASCADE
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
CREATE TABLE JobLocation
(
    QueryStr VARCHAR(70) NOT NULL,
    JobIdFK VARCHAR(10) NOT NULL,
    AddressStr VARCHAR(60) NOT NULL,
    City VARCHAR(30) NOT NULL,
    ZipCode VARCHAR(6),
    StateCode VARCHAR(2),
    Latitude DECIMAL(10,7),
    Longitude DECIMAL(10,7),
CONSTRAINT JobLocation_PK PRIMARY KEY (QueryStr),
CONSTRAINT JobLocation_FK1 FOREIGN KEY (JobIdFK) REFERENCES Job(JobId) ON DELETE CASCADE
);
CREATE TABLE UserLocation
(
    UserIdFk VARCHAR(36) NOT NULL,
    AddressStr VARCHAR(60) NOT NULL,
    City VARCHAR(30) NOT NULL,
    ZipCode VARCHAR(6),
    StateCode VARCHAR(2),
    Latitude DECIMAL(10,7),
    Longitude DECIMAL(10,7),
CONSTRAINT UserLocation_PK PRIMARY KEY (UserIdFk),
CONSTRAINT UserLocation_FK FOREIGN KEY (UserIdFk) REFERENCES User(UserId)
);
CREATE TABLE Resumes
(
    Id INT AUTO_INCREMENT,
    UserId VARCHAR(36) NOT NULL,
    FileName VARCHAR(255) NOT NULL,
    FileType VARCHAR(50) NOT NULL,
    FileContent LONGBLOB NOT NULL,
    FileText LONGBLOB NOT NULL,
    UploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT Resumes_PK PRIMARY KEY (id),
CONSTRAINT Resumes_FK FOREIGN KEY (UserId) REFERENCES User(UserId)
);
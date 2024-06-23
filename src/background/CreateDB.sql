DROP DATABASE IF EXISTS JOBDB;
CREATE DATABASE JOBDB;
USE JOBDB;

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

CREATE TABLE Job
(
    JobId VARCHAR(10) NOT NULL,
    Applicants TINYINT,
    BusinessOutlookRating DECIMAL(3, 2),
    CareerOpportunitiesRating DECIMAL(2, 1),
    CareerStage VARCHAR(20),
    CeoRating DECIMAL(3, 2),
    Company VARCHAR(50),
    CompensationAndBenefitsRating DECIMAL(2, 1),
    CultureAndValuesRating DECIMAL(2, 1),
    DiversityAndInclusionRating DECIMAL(2, 1),
    Job VARCHAR(100),
    -- uuid to keywords, one to many
    KeywordID VARCHAR(36),
    LocationStr VARCHAR(50),
    Mode VARCHAR(15),
    OverallRating DECIMAL(2, 1),
    PaymentBase DECIMAL(9, 2),
    PaymentFreq VARCHAR(8),
    PaymentHigh DECIMAL(9, 2),
    SecondsPostedAgo DECIMAL(7, 0),
    SeniorManagementRating DECIMAL(2, 1),
    WorkLifeBalanceRating DECIMAL(2, 1),
    TimeAdded timestamp default current_timestamp not null,
CONSTRAINT Job_PK PRIMARY KEY (JobId),
CONSTRAINT Job_foreign_key_keywords FOREIGN KEY (KeywordID) REFERENCES KeywordList(KeywordID)
ON DELETE CASCADE
);
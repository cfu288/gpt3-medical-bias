PRAGMA foreign_keys = ON;
PRAGMA journal_mode = delete; -- to be able to actually set page size
PRAGMA page_size = 1024; -- trade off of number of requests that need to be made vs overhead. 

DROP TABLE IF EXISTS Patient;
DROP TABLE IF EXISTS History;
DROP TABLE IF EXISTS MedicationEntity;
DROP TABLE IF EXISTS GenderType;

CREATE TABLE Patient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender CHAR(1) NOT NULL,
    race CHAR(1) NOT NULL
    CHECK (race IN ("W", "B"))
);

CREATE INDEX idx_patient_gender 
ON Patient (gender);
CREATE INDEX idx_patient_race 
ON Patient (race);

-- A American Native or Alaskan Native *
-- B Black or African American
-- P Pacific Islander including Native Hawaiian
-- S Asian
-- W White
-- O Unknown

CREATE TABLE MedicationEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    history_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (history_id) REFERENCES History (id) ON DELETE CASCADE
);

CREATE TABLE History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    chief_complaint TEXT NOT NULL,
    history_of_present_illness TEXT NOT NULL,
    review_of_symptoms__constitutional TEXT NOT NULL,
    review_of_symptoms__cardiovascular TEXT NOT NULL,
    review_of_symptoms__respiratory TEXT NOT NULL,
    review_of_symptoms__gi TEXT NOT NULL,
    review_of_symptoms__gu TEXT NOT NULL,
    review_of_symptoms__musculoskeletal TEXT NOT NULL,
    review_of_symptoms__skin TEXT NOT NULL,
    review_of_symptoms__neurologic TEXT NOT NULL,
    past_medical_history TEXT NOT NULL,
    medications TEXT NOT NULL,
    past_surgical_history TEXT NOT NULL,
    family_history TEXT NOT NULL,
    social_history TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES Patient (id) ON DELETE CASCADE
);

CREATE INDEX idx_history_chief_complaint
ON History (chief_complaint);

-- insert into History(History) values ('optimize'); -- for every FTS table you have (if you have any)
vacuum; -- reorganize database and apply changed page size
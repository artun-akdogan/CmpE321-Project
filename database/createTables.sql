-- Create department table if not exist. primary key is department_id
CREATE TABLE IF NOT EXISTS Department(
    department_id CHAR(100),
    department_name CHAR(100) UNIQUE,
    PRIMARY KEY (department_id)
);

-- Create department table if not exist. primary key is username.
-- department_id is referanced from Department table.
CREATE TABLE IF NOT EXISTS User(
    username CHAR(100),
    password CHAR(100),
    name CHAR(100),
    surname CHAR(100),
    email CHAR(100),
    department_id CHAR(100),
    PRIMARY KEY (username),
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
);

-- Create Database_Managers table if not exists.
CREATE TABLE IF NOT EXISTS Database_Managers(
    -- Creating a constraint to not allow more than 4 users.
    -- id should automaticly increase to count rows.
    username CHAR(100),
    password CHAR(100),
    PRIMARY KEY (username)
);

-- Delete triger if exists to prevent error.
drop trigger if exists chk_count;
-- This trigger will limit database row count to at most 4.
-- We will change delimiter temporarily to run trigger.
-- DELIMITER //
CREATE TRIGGER chk_count
BEFORE INSERT
ON Database_Managers
FOR EACH ROW
BEGIN
    -- Get count from database_managers
    SELECT COUNT(*) INTO @cnt FROM Database_Managers;
    IF @cnt > 3 THEN
        -- If count more or equal to 4, then send signal to interrupt insertion.
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No more than 4 managers are allowed';
    END IF;
END;
-- DELIMITER ;

-- Instructors table which is inherited from User table.
-- password,name,surname,email,department_id should be taken from Users table using username key.
CREATE TABLE IF NOT EXISTS Instructors(
    username CHAR(100),
    title CHAR(100),
    department_id CHAR(100),
    PRIMARY KEY (username),
    FOREIGN KEY (username) REFERENCES User(username)
    -- If we modify or delete in this table, we should also do them on User table.
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Classroom table to ensure 3NF in Course table
CREATE TABLE IF NOT EXISTS Classroom(
    classroom_id CHAR(100),
    campus CHAR(100),
    classroom_capacity INTEGER,
    PRIMARY KEY (classroom_id)
);

-- Create Course table if it does not exist. It would be both easier and convenient to check
-- prerequisites on server code. If we were using tables for prerequisires, then we could
-- check them by using the constraint: "CHECH(SUBSTR(prerequisite, -3)<SUBSTR(course_id, -3))".
-- campus and classroom_capacity should be taken from classroom table with classroom_id
-- department_id shuld be taken from users table using instructor_username
CREATE TABLE IF NOT EXISTS Course(
    course_id CHAR(100),
    name CHAR(100),
    course_code INTEGER,
    credits INTEGER,
    instructor_username CHAR(100),
    classroom_id CHAR(100),
    -- This line will ensure that slot value wil be between 1<=slot<=10
    slot INTEGER CHECK(slot>0 and slot<11),
    quota INTEGER,
    -- Prerequisites will be used as JSON_ARRAY
    prerequisites CHAR(100),
    -- This line will ensure that clasroom_id, and slot pairs are unique in each query
    UNIQUE KEY class_time (classroom_id, slot),
    PRIMARY KEY (course_id),
    FOREIGN KEY (instructor_username) REFERENCES Instructors(username),
    FOREIGN KEY (classroom_id) REFERENCES Classroom (classroom_id) 
);

-- Students table which is inherited from User table.
-- password,name,surname,email,department_id should be taken from Users table using username key.
CREATE TABLE IF NOT EXISTS Students(
    username CHAR(100),
    student_id INTEGER,
    -- added_courses will be used as JSON_ARRAY
    added_courses CHAR(100),
    PRIMARY KEY (student_id),
    FOREIGN KEY (username) REFERENCES User(username)
    -- If we modify or delete in this table, we should also do them on User table.
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Grades table if not exist. primary keys are student_id and course_id,
-- which are also referanced from other tables.
CREATE TABLE IF NOT EXISTS Grades(
    student_id INTEGER,
    course_id CHAR(100),
    grade FLOAT,
    PRIMARY KEY (course_id, student_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id) 
);
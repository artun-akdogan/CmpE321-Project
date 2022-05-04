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

-- Instructors table which is inherited from User table.
-- password,name,surname,email,department_id should be taken from Users table using username key.
CREATE TABLE IF NOT EXISTS Instructors(
    username CHAR(100),
    title CHAR(100) CHECK (title IN ('Assistant Professor','Associate Professor','Professor')),
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
    prerequisites JSON,
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
    added_courses JSON,
    completed_credits INT DEFAULT 0,
    gpa FLOAT DEFAULT NULL,
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

-- Create a procedure "filter" if it does not exist.
-- Take the 4 parameters, then filter the data based on those.
DROP PROCEDURE IF EXISTS filter;
CREATE PROCEDURE filter( IN department_id CHAR(100), 
                        IN campus CHAR(100), 
                        IN min_credit INT, 
                        IN max_credit INT)
BEGIN
    SELECT c.course_id, c.name, u.surname, i.department_id, c.credits, c.classroom_id, c.slot,
        c.quota, c.prerequisites
    FROM Course c, User u, Instructors i, Classroom s
    WHERE s.campus=campus and s.classroom_id=c.classroom_id and c.instructor_username=i.username
        and u.username=i.username and i.department_id=department_id and min_credit <= c.credits and c.credits <= max_credit;
END;

-- Delete triger if exists to prevent error.
drop TRIGGER if exists chk_count;
-- This trigger will limit database row count to at most 4.
CREATE TRIGGER chk_count BEFORE INSERT ON Database_Managers FOR EACH ROW
BEGIN
    -- Get count from database_managers
    SELECT COUNT(*) INTO @cnt FROM Database_Managers;
    IF @cnt > 3 THEN
        -- If count more or equal to 4, then send signal to interrupt insertion.
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No more than 4 managers are allowed';
    END IF;
END;

-- Delete triger if exists to prevent error.
DROP TRIGGER IF EXISTS chk_quota;
-- This trigger checks the relation between quota and classrom capacity.
-- It checks and gives error if there is conflict between them.
CREATE TRIGGER chk_quota BEFORE INSERT ON Course FOR EACH ROW
BEGIN
    SELECT s.classroom_capacity INTO @capacity FROM Classroom s
        WHERE NEW.classroom_id=s.classroom_id;
    IF NEW.quota > @capacity THEN
        -- send signal to interrupt insertion.
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quota greater then classroom capacity';
    END IF;
END;

-- Delete triger if exists to prevent error.
DROP TRIGGER IF EXISTS chk_student;
-- This trigger sets the gpa with the calculation given whenever
-- there is an insertion to the talble grades.
CREATE TRIGGER chk_student AFTER INSERT ON Grades FOR EACH ROW
BEGIN
    SELECT SUM(c.credits), SUM(c.credits*g.grade)/SUM(c.credits) INTO @credits, @gpa
        FROM Course c, Grades g
        WHERE NEW.student_id=g.student_id and g.course_id=c.course_id
        GROUP BY New.student_id;
    UPDATE Students SET completed_credits=@credits, gpa=@gpa WHERE NEW.student_id=student_id;
END;

#This script will initialize boun_database.

# Warning: Following lines that set enviroment variables should be secured in another file
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db_utils import hash

os.environ["MYSQL_DATABASE"] = "boun_database"
os.environ["MYSQL_USER"] = "project_3"
os.environ["MYSQL_PASSWORD"] = "secret"
os.environ["MYSQL_HOST"] = "localhost"
# End of Warning

import mysql.connector
import environ

env = environ.Env()
environ.Env.read_env()

# this credentials is needed to connect to the database.
connection = mysql.connector.connect(
  host=env("MYSQL_HOST"),
  user=env("MYSQL_USER"),
  password=env("MYSQL_PASSWORD"),
  database=env("MYSQL_DATABASE"),
  auth_plugin='mysql_native_password'
)

# cursor is connected to the database and ready to execute commands.
cursor= connection.cursor()
# Drop previous tables if exists:
print("Dropping previosly created tables ...")
cursor.execute("DROP TABLE IF EXISTS Students,Course,Classroom,Instructors,Database_Managers,Grades,User,Department;")
# Run createTables.sql which includes all the commands that forms the database.
print("Running createTables.sql ...")
with open('createTables.sql', 'r') as f: # reading file 
    for result in cursor.execute(f.read(), multi=True):
        if result.with_rows:
            print(result.fetchall())
# the code required to process the commands we run to the database. 
connection.commit()

print("Inserting example variables ...")
# TODO: insert initial database values.
# Here executescript can be used instead, we executed all the insertion by one by
cursor.execute(f'INSERT IGNORE INTO Database_Managers VALUES ("admin","{hash("password")}");')
cursor.execute('INSERT IGNORE INTO Department VALUES ("CMPE","Computer Engineering");')
# Here the hashed version of the passwords are stored as requested
cursor.execute(f'INSERT IGNORE INTO User VALUES ("student","{hash("password")}", "name", "surname", "student@example.com", "CMPE");')
cursor.execute(f'INSERT IGNORE INTO User VALUES ("senior","{hash("password")}", "senior", "student", "senior@example.com", "CMPE");')
cursor.execute(f'INSERT IGNORE INTO User VALUES ("instructor","{hash("password")}", "name", "surname", "instructor@example.com", "CMPE");')
cursor.execute('INSERT IGNORE INTO Instructors VALUES ("instructor", "professor", "CMPE");')
cursor.execute('INSERT IGNORE INTO Students VALUES ("student", 123, JSON_ARRAY(\'CMPE160\'), DEFAULT, DEFAULT);')
cursor.execute('INSERT IGNORE INTO Students VALUES ("senior", 234, JSON_ARRAY(\'CMPE250\'), DEFAULT, DEFAULT);')
cursor.execute('INSERT IGNORE INTO Classroom VALUES ("B2", "North", "100");')
cursor.execute('INSERT IGNORE INTO Classroom VALUES ("A2", "North", "100");')
cursor.execute('INSERT IGNORE INTO Course VALUES ("CMPE150", "CMPE", 150, 3, "instructor", "B2", 1, 100, JSON_ARRAY());')
cursor.execute('INSERT IGNORE INTO Course VALUES ("CMPE160", "CMPE", 160, 4, "instructor", "A2", 1, 50, JSON_ARRAY());')
cursor.execute('INSERT IGNORE INTO Grades VALUES (123, "CMPE150", 3.0);')
cursor.execute('INSERT IGNORE INTO Grades VALUES (234, "CMPE160", 3.5);')
cursor.execute('INSERT IGNORE INTO Grades VALUES (234, "CMPE150", 3.0);')

# Again the commitment code to synchronize the database
connection.commit()

print("Success!")

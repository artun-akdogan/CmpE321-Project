#This script will initialize boun_database.

# Warning: Following lines that set enviroment variables should be secured in another file
import os

os.environ["MYSQL_DATABASE"] = "boun_database"
os.environ["MYSQL_USER"] = "project_3"
os.environ["MYSQL_PASSWORD"] = "secret"
os.environ["MYSQL_HOST"] = "localhost"
# End of Warning

import mysql.connector
import environ

env = environ.Env()
environ.Env.read_env()

connection = mysql.connector.connect(
  host=env("MYSQL_HOST"),
  user=env("MYSQL_USER"),
  password=env("MYSQL_PASSWORD"),
  database=env("MYSQL_DATABASE"),
  auth_plugin='mysql_native_password'
)

cursor= connection.cursor()

# Run createTables.sql
print("Running createTables.sql ...")
with open('createTables.sql', 'r') as f:
    for result in cursor.execute(f.read(), multi=True):
        if result.with_rows:
            print(result.fetchall())
    
connection.commit()

print("Inserting default variables ...")
# TODO: insert initial database values.
cursor.execute('INSERT IGNORE INTO Database_Managers VALUES ("admin","password");')
cursor.execute('INSERT IGNORE INTO Department VALUES ("CMPE","Computer Engineering");')
cursor.execute('INSERT IGNORE INTO User VALUES ("student","password", "name", "surname", "student@example.com", "CMPE");')
cursor.execute('INSERT IGNORE INTO User VALUES ("instructor","password", "name", "surname", "instructor@example.com", "CMPE");')
cursor.execute('INSERT IGNORE INTO Instructors VALUES ("instructor", "professor", "CMPE");')
cursor.execute('INSERT IGNORE INTO Students VALUES ("student", 123, "");')

connection.commit()

print("Success!")
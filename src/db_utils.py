from django.db import connection
import hashlib
import json

# To execute a query and return the result of that query. 
# We always needed to use this function. 
def run_statement(statement):
    cursor= connection.cursor()
    cursor.execute(statement)
    return cursor.fetchall()

# Hash the password as wanted, this code is executed.
def hash(password):
    return hashlib.sha256(password.encode('UTF-8')).hexdigest()

# this is shortcut to parse strings.
def parse(string):
    return json.loads(string)

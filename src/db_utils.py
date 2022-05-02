from django.db import connection
import hashlib

def run_statement(statement):
    cursor= connection.cursor()
    cursor.execute(statement)
    return cursor.fetchall()

def hash(password):
    return hashlib.sha256(password.encode('UTF-8')).hexdigest()
    

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement

def login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]

    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../database_managers') #Redirect user to home page
    else:
        return HttpResponseRedirect('../?fail=true')

def homePage(req):
    #result=run_statement(f"SELECT * FROM Post;") #Run the query in DB
    
    username=req.session["username"] #Retrieve the username of the logged-in user
    action = req.GET.get("action", 0) #Check the value of the GET parameter
    try: action = int(action)
    except: action = 0
    #isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    return render(req,'databaseManager.html',{"username":username, "action": action})

def createUser(req):
    username = req.POST["username"]
    password = req.POST["password"]
    name = req.POST["name"]
    surname = req.POST["surname"]
    email = req.POST["email"]
    department_id = req.POST["department_id"]
    user_type = req.POST["type"]
    title = req.POST["title"]
    student_id = req.POST["student_id"]

    result=run_statement(f"INSERT INTO User VALUES(\"{username}\", \"{password}\", \"{name}\", \"{surname}\", \"{email}\", \"{department_id}\");")
    if(user_type=="instructor"):
        result=run_statement(f"INSERT INTO Instructors VALUES(\"{username}\", \"{title}\", \"{department_id}\");")
    else:
        result=run_statement(f"INSERT INTO Students VALUES(\"{username}\", {student_id}, \"\");")
    return HttpResponseRedirect('../database_managers?action=1')

def deleteStudent(req):
    student_id = req.POST["student_id"]
    result=run_statement(f"DELETE FROM Students WHERE student_id={student_id};")
    return HttpResponseRedirect('../database_managers?action=1')

def updateInstructor(req):
    username = req.POST["username"]
    title = req.POST["title"]
    result=run_statement(f"UPDATE Instructors SET title={title} WHERE username={username};")
    return HttpResponseRedirect('../database_managers?action=1')
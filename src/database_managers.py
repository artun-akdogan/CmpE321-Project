
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement, hash

def login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]

    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}' and password='{hash(password)}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../database_managers') #Redirect user to home page
    else:
        return HttpResponseRedirect('../?fail=true')

def homePage(req):
    students=run_statement(f"SELECT u.username, u.name, u.surname, u.email, u.department_id,\
        s.completed_credits, s.gpa FROM User u, Students s WHERE s.username=u.username\
        ORDER BY s.completed_credits;")
    instructors=run_statement(f"SELECT u.username, u.name, u.surname, u.email, u.department_id, i.title\
        FROM User u, Instructors i WHERE i.username=u.username;")
    username=req.session["username"] #Retrieve the username of the logged-in user
    action = req.GET.get("action", 0) #Check the value of the GET parameter
    try: action = int(action)
    except: action = 0
    #isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    return render(req,'databaseManager.html',{"username":username, "action": action, "students": students, "instructors":instructors})

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

    result=run_statement(f"INSERT INTO User VALUES(\"{username}\", \"{hash(password)}\", \"{name}\", \"{surname}\", \"{email}\", \"{department_id}\");")
    if(user_type=="instructor"):
        result=run_statement(f"INSERT INTO Instructors VALUES(\"{username}\", \"{title}\", \"{department_id}\");")
    else:
        result=run_statement(f"INSERT INTO Students VALUES(\"{username}\", {student_id}, JSON_ARRAY());")
    return HttpResponseRedirect('../database_managers?action=1')

def deleteStudent(req):
    student_id = req.POST["student_id"]
    result=run_statement(f"DELETE FROM Students WHERE student_id=\"{student_id}\";")
    return HttpResponseRedirect('../database_managers?action=1')

def updateInstructor(req):
    username = req.POST["username"]
    title = req.POST["title"]
    result=run_statement(f"UPDATE Instructors SET title=\"{title}\" WHERE username=\"{username}\";")
    return HttpResponseRedirect('../database_managers?action=1')

def getStudent(req):
    student_id = req.POST["student_id"]
    data=run_statement(f"SELECT g.course_id, c.name, g.grade\
        FROM Grades g, Course c WHERE g.student_id=\"{student_id}\" and c.course_id=g.course_id;")
    return render(req,'table.html', {"title": f"Student {student_id}'s grades:", 
        "headers": ("Course ID", "Course Name", "Grade"), "data": data})

def getInstructor(req):
    username = req.POST["username"]
    data=run_statement(f"SELECT c.course_id, c.name, c.classroom_id, s.campus, c.slot\
        FROM Course c, Classroom s WHERE c.instructor_username=\"{username}\" and c.classroom_id=s.classroom_id;")
    return render(req,'table.html', {"title": f"Instructor {username}'s courses:", 
        "headers": ("Course ID", "Course Name", "Classroom ID", "Campus", "Time Slot"), "data": data})
        
def getCourse(req):
    course_id = req.POST["course_id"].upper()
    data=run_statement(f"SELECT c.course_id, c.name, SUM(g.grade)/COUNT(g.course_id)\
        FROM Course c, Grades g WHERE g.course_id=\"{course_id}\" and g.course_id=c.course_id\
        GROUP BY g.course_id;")
    return render(req,'table.html', {"title": f"", 
        "headers": ("Course ID", "Course Name", "Average Grade"), "data": data})

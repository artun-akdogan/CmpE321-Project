
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement, hash

def login(req):
    #Retrieve data from the request body
    # To login, first we post the credentials,
    username=req.POST["username"]
    password=req.POST["password"]
    # then we look for a tuple who satisfies those credentials. 
    # PS: run_statement is just to execute that query and return the result.
    # Here again we need to compare the hashed version of the password with the database.
    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}' and password='{hash(password)}';") #Run the query in DB

    if result: 
         # If a result is retrieved, we save our username in the session in case it is needed
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../database_managers') #Then, redirect user to home page
    else:
        # If there is no tuple like that, we set the "fail" as true.
        return HttpResponseRedirect('../?fail=true')

# Note that action==1 if Operation completed successfully, 
# and action==2 if Operation failed. None if any other.
def homePage(req):
    # students is the result of that query.
    students=run_statement(f"SELECT u.username, u.name, u.surname, u.email, u.department_id,\
        s.completed_credits, s.gpa FROM User u, Students s WHERE s.username=u.username\
        ORDER BY s.completed_credits;")
    instructors=run_statement(f"SELECT u.username, u.name, u.surname, u.email, u.department_id, i.title\
        FROM User u, Instructors i WHERE i.username=u.username;")
    # Fetching username from session.
    username=req.session["username"] #Retrieve the username of the logged-in user
    action = req.GET.get("action", 0) #Check the value of the GET parameter
    try: action = int(action)
    except: action = 0
    #isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    return render(req,'databaseManager.html',{"username":username, "action": action, "students": students, "instructors":instructors})

def createUser(req):
    try:
        # To create a user, we need to first collect data. After the user posted that credentials, we need to insert that tuple into the database.
        username = req.POST["username"]
        password = req.POST["password"]
        name = req.POST["name"]
        surname = req.POST["surname"]
        email = req.POST["email"]
        department_id = req.POST["department_id"]
        user_type = req.POST["type"]
        title = req.POST["title"]
        student_id = int(req.POST["student_id"])
        # Insertion of that tuple is executed in this way.
        result=run_statement(f"INSERT INTO User VALUES(\"{username}\", \"{hash(password)}\", \"{name}\", \"{surname}\", \"{email}\", \"{department_id}\");")
        # We need to also add the tuple into the table instructors or students.
        if(user_type=="instructor"):
            result=run_statement(f"INSERT INTO Instructors VALUES(\"{username}\", \"{title}\", \"{department_id}\");")
        else:
            result=run_statement(f"INSERT INTO Students VALUES(\"{username}\", {student_id}, JSON_ARRAY(), DEFAULT, DEFAULT);")
        return HttpResponseRedirect('../database_managers?action=1')
    except: pass
    return HttpResponseRedirect('../database_managers?action=2')

def deleteStudent(req):
    try:
        # To delete a user, we just need to student_id of the user.
        student_id = req.POST["student_id"]
        # After collecting that information, we just need to execute this query.
        result=run_statement(f"DELETE FROM Students WHERE student_id=\"{student_id}\";")
        # Then set action equals 1.
        return HttpResponseRedirect('../database_managers?action=1')
    except: pass
    return HttpResponseRedirect('../database_managers?action=2')

def updateInstructor(req):
    try:
        # To update an instructor, we do the same thing. Collect data, execute query with that data.
        username = req.POST["username"]
        title = req.POST["title"]
        result=run_statement(f"UPDATE Instructors SET title=\"{title}\" WHERE username=\"{username}\";")
        return HttpResponseRedirect('../database_managers?action=1') 
    except: pass
    return HttpResponseRedirect('../database_managers?action=2')

def getStudent(req):
    # To get a student, we do the same thing. Collect data, execute query with that data.
    student_id = req.POST["student_id"]
    data=run_statement(f"SELECT g.course_id, c.name, g.grade\
        FROM Grades g, Course c WHERE g.student_id=\"{student_id}\" and c.course_id=g.course_id;")
    return render(req,'table.html', {"title": f"Student {student_id}'s grades:", 
        "headers": ("Course ID", "Course Name", "Grade"), "data": data})

def getInstructor(req):
    # To get an instructor, we do the same thing. Collect data, execute query with that data.
    username = req.POST["username"]
    data=run_statement(f"SELECT c.course_id, c.name, c.classroom_id, s.campus, c.slot\
        FROM Course c, Classroom s WHERE c.instructor_username=\"{username}\" and c.classroom_id=s.classroom_id;")
    return render(req,'table.html', {"title": f"Instructor {username}'s courses:", 
        "headers": ("Course ID", "Course Name", "Classroom ID", "Campus", "Time Slot"), "data": data})
        
def getCourse(req):
    # To get a course, we do the same thing. Collect data, execute query with that data.
    course_id = req.POST["course_id"].upper()
    data=run_statement(f"SELECT c.course_id, c.name, SUM(g.grade)/COUNT(g.course_id)\
        FROM Course c, Grades g WHERE g.course_id=\"{course_id}\" and g.course_id=c.course_id\
        GROUP BY g.course_id;")
    return render(req,'table.html', {"title": f"", 
        "headers": ("Course ID", "Course Name", "Average Grade"), "data": data})

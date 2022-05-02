
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement

def homePage(req):
    #result=run_statement(f"SELECT * FROM Post;") #Run the query in DB
    
    username=req.session["username"] #Retrieve the username of the logged-in user
    action = req.GET.get("action", 0) #Check the value of the GET parameter
    try: action = int(action)
    except: action = 0

    return render(req,'instructor.html',{"username":username, "action": action})

def getClassroom(req):
    slot = req.POST['slot']
    try: slot = int(slot)
    except: return render(req, "table.html", {})
    data = run_statement(f"SELECT s.* FROM Classroom s, Course c WHERE s.classroom_id=c.classroom_id and c.slot!={slot}")
    return render(req, "table.html", {"title": f"Classes available on timeslot {slot}:", 
        "headers": ("Classroom ID", "Campus", "Classroom Capacity"), "data": data})

def createCourse(req):
    try:
        username=req.session["username"] 
        course_id = req.POST['course_id']
        name = req.POST['name']
        course_code = int(course_id[-3:])
        credits = int(req.POST['credits'])
        classroom_id = req.POST['classroom_id']
        time_slot = int(req.POST['time_slot'])
        quota = int(req.POST['quota'])
        data = run_statement(f"INSERT INTO Course VALUES(\'{course_id}\', \'{name}\', {course_code}, {credits},\
            \'{username}\', \'{classroom_id}\', {time_slot}, {quota}, JSON_ARRAY())")
    except Exception:
        return HttpResponseRedirect('../instructors?action=2')
    
    return HttpResponseRedirect('../instructors?action=1')
    
def addPrerequisite(req):
    course_id = req.POST['course_id']
    prerequisite = req.POST['prerequisite']
    #print(run_statement(f"SELECT JSON_ARRAY_APPEND(prerequisites, '$', \'{prerequisite}\') FROM Course WHERE course_id=\'{course_id}\')"))
    data = run_statement(f"UPDATE Course SET prerequisites=JSON_ARRAY_APPEND(prerequisites, '$', \'{prerequisite}\') WHERE course_id=\'{course_id}\'")
    
    return HttpResponseRedirect('../instructors?action=1')
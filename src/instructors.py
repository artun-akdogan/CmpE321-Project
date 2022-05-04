
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement

# Note that action==1 if Operation completed successfully, 
# and action==2 if Operation failed. None if any other.
def homePage(req):
    username=req.session["username"] #Retrieve the username of the logged-in user
    action = req.GET.get("action", 0) #Check the value of the GET parameter
    try: action = int(action)
    except: action = 0

    courses=run_statement(f"SELECT course_id, name, classroom_id, slot, quota, prerequisites\
        FROM Course WHERE instructor_username=\'{username}\'")
    # Remove square brackets
    courses = list(map(lambda i: i[:-1] + tuple([i[-1][1:-1].replace("\"", "")]), courses))

    return render(req,'instructor.html',{"username": username, "action": action, "courses": courses})

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
        course_id = req.POST['course_id'].upper()
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
    try:
        course_id = req.POST['course_id'].upper()
        prerequisite = req.POST['prerequisite'].upper()
        course_code = int(course_id[-3:])
        prerequisite_code = int(prerequisite[-3:])
        # Check if prerequisite valid, then try to append the new prerequisite
        if course_code>prerequisite_code and run_statement(f"SELECT * FROM Course WHERE course_id=\"{prerequisite}\""):
            data = run_statement(f"UPDATE Course SET prerequisites=JSON_ARRAY_APPEND(prerequisites, '$', \'{prerequisite}\') \
                WHERE course_id=\'{course_id}\' and not JSON_CONTAINS(prerequisites, \'\"{prerequisite}\"\', \'$\')")
    
            return HttpResponseRedirect('../instructors?action=1')
    except: pass
    return HttpResponseRedirect('../instructors?action=2')

def getStudents(req):
    course_id = req.POST['course_id'].upper()
    username=req.session["username"] 
    
    data = run_statement(f"SELECT u.username, s.student_id, u.email, u.name, u.surname \
        FROM User u, Students s, Course c WHERE c.course_id=\"{course_id}\" and c.instructor_username=\"{username}\" \
        and u.username=s.username and JSON_CONTAINS(s.added_courses, \'\"{course_id}\"\', \'$\')")

    return render(req, "table.html", {"title":f"Students added the course {course_id}:", 
        "headers":("Username", "Student ID", "Email", "Name", "Surname"), "data":data})

def changeCourse(req):
    try:
        course_id = req.POST['course_id'].upper()
        name = req.POST['name']
        username=req.session["username"] 

        run_statement(f"UPDATE Course SET name=\"{name}\" WHERE course_id=\"{course_id}\" and instructor_username=\"{username}\"")
        return HttpResponseRedirect('../instructors?action=1')
    except: pass
    return HttpResponseRedirect('../instructors?action=2')


def enterGrade(req):
    try:
        course_id = req.POST['course_id'].upper()
        student_id = int(req.POST['student_id'])
        grade = float(req.POST['grade'])
        run_statement(f"UPDATE Students SET added_courses=JSON_REMOVE(added_courses, \
            JSON_UNQUOTE(JSON_SEARCH(added_courses, 'all', \"{course_id}\"))) WHERE student_id={student_id}")
        run_statement(f"INSERT INTO Grades VALUES({student_id},\"{course_id}\",{grade})")

        return HttpResponseRedirect('../instructors?action=1')
    except: pass
    return HttpResponseRedirect('../instructors?action=2')

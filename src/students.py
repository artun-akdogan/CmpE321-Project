
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement, parse

def homePage(req):
    
    username=req.session["username"] #Retrieve the username of the logged-in user
    action = req.GET.get("action", 0) #Check the value of the GET parameter
    try: action = int(action)
    except: action = 0

    
    courses=run_statement(f"SELECT c.course_id, c.name, u.surname, i.department_id, c.credits, c.classroom_id, c.slot,\
        c.quota, c.prerequisites FROM Course c, Instructors i, User u WHERE c.instructor_username=i.username and i.username=u.username")
    # Remove square brackets and quotes
    courses = list(map(lambda i: i[:-1] + tuple([i[-1][1:-1].replace("\"", "")]), courses))

    return render(req,'student.html',{"username":username, "action": action, "courses": courses})

def addCourse(req):
    try:
        username = req.session["username"] #Retrieve the username of the logged-in user
        course_id = req.POST["course_id"].upper()

        # Check if student took the course before
        if not run_statement(f"SELECT * FROM Grades g, Students s WHERE s.username=\"{username}\" and s.student_id=g.student_id and g.course_id=\"{course_id}\""):
            prerequisites = parse(run_statement(f"SELECT prerequisites FROM Course WHERE course_id=\"{course_id}\"")[0][0])
            cnt=0
            for course in prerequisites:
                if run_statement(f"SELECT g.course_id FROM Grades g, Students s WHERE s.username=\'{username}\' and g.student_id=s.student_id and g.course_id=\'{course}\'"):
                    cnt+=1
            if cnt==len(prerequisites):
                # Check quota and if course was added successfully before
                if run_statement(f"Select * FROM Students as s, Course as c WHERE s.username=\"{username}\" and c.course_id=\"{course_id}\" and \
                            not JSON_CONTAINS(s.added_courses, \'\"{course_id}\"\', \'$\') and \
                            (SELECT COUNT(*) FROM Students WHERE JSON_CONTAINS(added_courses, '\"{course_id}\"', '$')) < c.quota"):
                        
                    run_statement(f"UPDATE Students SET added_courses=JSON_ARRAY_APPEND(added_courses, '$', \'{course_id}\') \
                        WHERE s.username=\"{username}\"")
                    return HttpResponseRedirect('../students?action=1')
    except:
        pass
    
    return HttpResponseRedirect('../students?action=2')

    

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement, parse

def homePage(req):
    
    
    username=req.session["username"] #Retrieve the username of the logged-in user
    action = req.GET.get("action", 0) #Check the value of the GET parameter
    try: action = int(action)
    except: action = 0
    
    taken = run_statement(f"SELECT c.course_id, c.name, g.grade FROM Course c, Grades g, Students s WHERE \
        s.username=\"{username}\" and s.student_id=g.student_id and c.course_id=g.course_id")

    for course in parse(run_statement(f"SELECT added_courses FROM Students WHERE username=\"{username}\"")[0][0]):
        taken = run_statement(f"Select course_id, name, null FROM Course WHERE course_id=\'{course}\'") + taken
    
    courses=run_statement(f"SELECT c.course_id, c.name, u.surname, i.department_id, c.credits, c.classroom_id, c.slot,\
        c.quota, c.prerequisites FROM Course c, Instructors i, User u WHERE c.instructor_username=i.username and i.username=u.username")

    # Remove square brackets and quotes
    courses = list(map(lambda i: i[:-1] + tuple([i[-1][1:-1].replace("\"", "")]), courses))

    return render(req,'student.html',{"username":username, "action": action, "courses": courses, "taken": taken})

def addCourse(req):
    # To add course.
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
                if run_statement(f"Select * FROM Students s, Course c WHERE s.username=\"{username}\" and c.course_id=\"{course_id}\" and \
                            not JSON_CONTAINS(s.added_courses, \'\"{course_id}\"\', \'$\') and \
                            (SELECT COUNT(*) FROM Students WHERE JSON_CONTAINS(added_courses, '\"{course_id}\"', '$')) < c.quota"):
                        
                    run_statement(f"UPDATE Students SET added_courses=JSON_ARRAY_APPEND(added_courses, '$', \'{course_id}\') \
                        WHERE username=\"{username}\"")
                    return HttpResponseRedirect('../students?action=1')
    except:
        pass
    
    return HttpResponseRedirect('../students?action=2')

def search(req):
    # To search with the keyword(regex can be used here)
    keyword = req.POST["keyword"]    
    data=run_statement(f"SELECT c.course_id, c.name, u.surname, i.department_id, c.credits, c.classroom_id, c.slot,\
        c.quota, c.prerequisites FROM Course c, Instructors i, User u WHERE c.instructor_username=i.username and i.username=u.username\
        and c.name REGEXP '{keyword}'")

    # Remove square brackets and quotes
    data = list(map(lambda i: i[:-1] + tuple([i[-1][1:-1].replace("\"", "")]), data))

    
    return render(req,'table.html',{"title":f"Courses containing keyword {keyword}:", "headers": ("Course ID", "Course Name", "Instructor Surname", 
        "Department", "Credits", "Classroom ID", "Time Slot", "Quota", "Prerequisites"), "data": data})

'''
PS: "filter" procedure
CREATE PROCEDURE filter( IN department_id CHAR(100), 
                        IN campus CHAR(100), 
                        IN min_credit INT, 
                        IN max_credit INT)
BEGIN
    SELECT c.course_id, c.name, u.surname, i.department_id, c.credits, c.classroom_id, c.slot,
        c.quota, c.prerequisites
    FROM Course c, User u, Instructors i, Classroom s
    WHERE s.campus=campus and s.classroom_id=c.classroom_id and c.instructor_username=i.username
        and u.username=i.username and i.department_id=department_id and min_credit <= c.credits and c.credits <= max_credit;
END;
'''

def filter(req):
    # To filter the results, firstly we need to collect the parameters.
    department_id = req.POST["department_id"]
    campus = req.POST["campus"]
    min_credit = req.POST["min_credit"]
    max_credit = req.POST["max_credit"]
    # Then call the filter function with the parameters.
    data = run_statement(f"CALL filter(\'{department_id}\',\'{campus}\',{min_credit},{max_credit})")
    
    return render(req,'table.html',{"title":f"Courses filtered:", "headers": ("Course ID", "Course Name", "Instructor Surname", 
        "Department", "Credits", "Classroom ID", "Time Slot", "Quota", "Prerequisites"), "data": data})

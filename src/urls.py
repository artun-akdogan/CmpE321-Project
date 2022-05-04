from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import *
from .db_utils import run_statement, hash
from . import database_managers
from . import instructors
from . import students

def index(req):
    #Logout the user if logged 
    if req.session:
        req.session.flush()
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'loginIndex.html',{"login_form":loginForm,"action_fail":isFailed})

def login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]

    result=run_statement(f"SELECT * FROM User WHERE username='{username}' and password='{hash(password)}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        is_instructor = run_statement(f"SELECT * FROM Instructors WHERE username='{username}';")
        if is_instructor:
            return HttpResponseRedirect('../instructors') #Redirect user to home page
        is_student = run_statement(f"SELECT * FROM Students WHERE username='{username}';")
        if is_student:
            return HttpResponseRedirect('../students') #Redirect user to home page
        
    
    return HttpResponseRedirect('../?fail=true')

urlpatterns = [
    path('', index, name='index'),
    path('database_managers', database_managers.homePage, name="database_managers"),
    path('database_managers/create_user', database_managers.createUser, name="createUser"),
    path('database_managers/delete_student', database_managers.deleteStudent, name="deleteStudent"),
    path('database_managers/update_instructor', database_managers.updateInstructor, name="updateInstructor"),
    path('database_managers/get_student', database_managers.getStudent, name="getStudent"),
    path('database_managers/get_instructor', database_managers.getInstructor, name="getInstructor"),
    path('database_managers/get_course', database_managers.getCourse, name="getCourse"),
    path('instructors', instructors.homePage, name="instructors"),
    path('instructors/get_classroom', instructors.getClassroom, name="getClassroom"),
    path('instructors/create_course', instructors.createCourse, name="createCourse"),
    path('instructors/add_prerequisite', instructors.addPrerequisite, name="addPrerequisite"),
    path('instructors/get_students', instructors.getStudents, name="getStudentsInstructor"),
    path('instructors/change_course', instructors.changeCourse, name="changeCourse"),
    path('instructors/enter_grade', instructors.enterGrade, name="enterGrade"),
    path('students', students.homePage, name="students"),
    path('students/add_course', students.addCourse, name="addCourse"),
    path('students/search', students.search, name="search"),
    path('students/filter', students.filter, name="filter"),
    path('login/database_manager', database_managers.login, name="login_database_manager"),
    path('login/user', login, name="login"),
]

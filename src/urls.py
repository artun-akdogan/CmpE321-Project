from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import *
from .db_utils import run_statement
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

    result=run_statement(f"SELECT * FROM User WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        is_instructor = run_statement(f"SELECT * FROM Instructors WHERE username='{username}';")
        if is_instructor:
            return HttpResponseRedirect('../instructors') #Redirect user to home page
        is_student = run_statement(f"SELECT * FROM Students WHERE username='{username}';")
        if is_student:
            return HttpResponseRedirect('../students') #Redirect user to home page
        
    
    return HttpResponseRedirect('../?fail=true')

"""
def createPost(req):
    #Retrieve data from the request body
    title=req.POST["title"]
    body=req.POST["body"]
    logged_user=req.session["username"]
    try:
        run_statement(f"CALL CreatePost('{title}','{body}','{logged_user}')")
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')
"""

urlpatterns = [
    path('', index, name='index'),
    path('database_managers', database_managers.homePage, name="database_managers"),
    path('instructors', instructors.homePage, name="instructors"),
    path('students', students.homePage, name="students"),
    path('login/database_manager', database_managers.login, name="login_database_manager"),
    path('login/user', login, name="login"),
    #path('createPost', createPost,name="createPost"),
]

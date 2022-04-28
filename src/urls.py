from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import *
from .db_utils import run_statement

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

    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../?fail=true')

def homePage(req):
    #result=run_statement(f"SELECT * FROM Post;") #Run the query in DB
    
    username=req.session["username"] #Retrieve the username of the logged-in user
    #isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'userHome.html',{"username":username})

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
    path('home', homePage, name="homePage"),
    path('login', login, name="login"),
    #path('createPost', createPost,name="createPost"),
]

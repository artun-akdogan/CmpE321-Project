
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
    #isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'databaseManager.html',{"username":username})

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .db_utils import run_statement

def homePage(req):
    #result=run_statement(f"SELECT * FROM Post;") #Run the query in DB
    
    username=req.session["username"] #Retrieve the username of the logged-in user
    #isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'instructor.html',{"username":username})
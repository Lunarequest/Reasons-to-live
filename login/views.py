from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages

# Create your views here.
def login_user(request):
    if request.method == "POST":
        username = request.POST["usrname"]
        password = request.POST["passwd"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/modrate")
        else:
            messages.info(request, "invalid login")
            return redirect("/login", locals())
    else:
        return render(request, "login/login.html")


def logouts(request):
    logout(request)
    return redirect("/")

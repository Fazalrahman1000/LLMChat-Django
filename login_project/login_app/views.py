from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Log the user in
            return redirect("chat_page")  # Redirects to the chat page
        else:
            return render(request, "login_app/login.html", {"error": "Invalid credentials"})
    return render(request, "login_app/login.html")

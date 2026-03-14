from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import UserProfile


def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            # If superuser → go to User Control Panel
            if user.is_superuser:
                return redirect("/user-control/")

            # Ensure UserProfile exists
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "role": "reporter"
                }
            )

            # Force password change
            if profile.must_change_password:
                return redirect("/change-password/")

            role = profile.role

            if role == "reporter":
                return redirect("/reporter-dashboard/")

            elif role == "subeditor":
                return redirect("/subeditor-dashboard/")

            elif role == "editor":
                return redirect("/editor-dashboard/")

            elif role == "paginator":
                return redirect("/pagination-dashboard/")

            return redirect("/")

        else:

            return render(request, "accounts/login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "accounts/login.html")

def user_logout(request):

    logout(request)

    return redirect('/login/')

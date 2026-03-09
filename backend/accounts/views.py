from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            # Get user role
            role = user.userprofile.role

            if role == 'reporter':
                return redirect('/reporter-dashboard/')

            elif role == 'subeditor':
                return redirect('/subeditor-dashboard/')

            elif role == 'editor':
                return redirect('/editor-dashboard/')

            elif role == 'paginator':
                return redirect('/pagination-dashboard/')

            else:
                return redirect('/')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


def user_logout(request):

    logout(request)

    return redirect('/login/')

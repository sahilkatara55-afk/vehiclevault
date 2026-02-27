from django.shortcuts import render, redirect
from .forms import UsersignupForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Signup View
def Usersignupview(request):

    if request.method == 'POST':

        form = UsersignupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')   # login url name
        else:
            return render(request, 'core/signup.html', {'form': form})

    else:
        form = UsersignupForm()
        return render(request, 'core/signup.html', {'form': form})


# Home
def home(request):
    return render(request, 'home.html')


# Login View
def userloginform(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Admin Check
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')

            # Normal User
            else:
                return redirect('user_dashboard')

        else:
            return render(request, 'core/login.html', {
                'error': 'Invalid Email or Password'
            })


    return render(request, 'core/login.html')


# User Dashboard
@login_required
def user_dashboard(request):
    return render(request, 'vehicles/user/user_dashboard.html')


# Admin Dashboard
@login_required
def admin_dashboard(request):
    return render(request, 'vehicles/admin/admin_dashboard.html')

# Logout View
def logout_user(request):
    logout(request)
    return redirect('login')
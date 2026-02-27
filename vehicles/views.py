from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import role_required

# Create your views here.
@role_required(allowed_roles=["admin"]) #check in core.urls.py login name should exist..
def adminDashboardView(request):
    return render(request,"vehicles/admin/admin_dashboard.html")

#@login_required(login_url="login")
@role_required(allowed_roles=["user"]) #check in core.urls.py login name should exist.. 
def userDashboardView(request):

    return render(request,"vehicles/user/user_dashboard.html")
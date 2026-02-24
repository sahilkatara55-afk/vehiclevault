from django.contrib import admin
from django.urls import include,path 
from .import views

urlpatterns = [
    path('', views.home, name='home'),      # Homepage
    path('home/', views.home, name='home'), # /home/
    path('signup/', views.Usersignupview, name='signup'),

]
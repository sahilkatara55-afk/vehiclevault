from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('signup/', views.Usersignupview, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('admin-request-pending/', views.admin_request_pending, name='admin_request_pending'),

    path('login/', views.userloginform, name='login'),

    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),

    path('my-account/', views.my_account, name='my_account'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin Signup Request Management
    path('admin-requests/', views.admin_requests_list, name='admin_requests_list'),
    path('admin-requests/<int:pk>/approve/', views.approve_admin_request, name='approve_admin_request'),
    path('admin-requests/<int:pk>/reject/', views.reject_admin_request, name='reject_admin_request'),

    path('logout/', views.logout_user, name='logout'),
]
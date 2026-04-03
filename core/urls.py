from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('signup/', views.Usersignupview, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('admin-request-pending/', views.admin_request_pending, name='admin_request_pending'),

    path('login/', views.userloginform, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),

    path('api/notifications/', views.user_notifications_api, name='user_notifications_api'),
    path('api/notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/delete/<int:pk>/', views.delete_notification, name='delete_notification'),

    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),

    path('my-account/', views.my_account, name='my_account'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Car Management
    path('manage-cars/', views.manage_cars, name='manage_cars'),
    path('manage-cars/add/', views.car_add, name='car_add'),
    path('manage-cars/edit/<int:pk>/', views.car_edit, name='car_edit'),
    path('manage-cars/delete/<int:pk>/', views.car_delete, name='car_delete'),

    # User Management
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/block/<int:pk>/', views.user_toggle_block, name='user_toggle_block'),
    path('manage-users/delete/<int:pk>/', views.user_delete_admin, name='user_delete_admin'),

    # Other Admin Sidebar Views
    path('manage-accessories/', views.manage_accessories, name='manage_accessories'),
    path('manage-accessories/add/', views.accessory_add, name='accessory_add'),
    path('manage-accessories/edit/<int:pk>/', views.accessory_edit, name='accessory_edit'),
    path('manage-accessories/delete/<int:pk>/', views.accessory_delete, name='accessory_delete'),
    path('admin-notifications/', views.admin_notifications, name='admin_notifications'),
    path('admin-reports/', views.admin_reports, name='admin_reports'),
    path('admin-settings/', views.admin_settings, name='admin_settings'),

    # Brand Management
    path('manage-brands/', views.manage_brands, name='manage_brands'),
    path('manage-brands/add/', views.brand_add, name='brand_add'),
    path('manage-brands/edit/<int:pk>/', views.brand_edit, name='brand_edit'),
    path('manage-brands/delete/<int:pk>/', views.brand_delete, name='brand_delete'),

    # Admin Signup Request Management
    path('admin-requests/', views.admin_requests_list, name='admin_requests_list'),
    path('admin-requests/<int:pk>/approve/', views.approve_admin_request, name='approve_admin_request'),
    path('admin-requests/<int:pk>/reject/', views.reject_admin_request, name='reject_admin_request'),

    path('logout/', views.logout_user, name='logout'),

    # Public Pages — Search, Brands, Compare, Details
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('expert-reviews/', views.expert_reviews, name='expert_reviews'),
    path('user-reviews/', views.user_reviews_page, name='user_reviews_page'),
    path('search/', views.search_cars, name='search_cars'),
    path('brands/', views.brands_view, name='brands'),
    path('brands/<str:make>/', views.brand_cars, name='brand_cars'),
    path('compare/', views.compare_cars, name='compare_cars'),
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
    path('api/analytics/', views.analytics_data_api, name='analytics_data_api'),
    path('admin-analytics/export/', views.export_analytics_csv, name='export_analytics_csv'),
    path('car/<int:pk>/', views.car_detail, name='car_detail'),
    path('car/<int:car_id>/review/', views.submit_review, name='submit_review'),
    path('car/<int:car_id>/enquiry/', views.submit_enquiry, name='submit_enquiry'),
    path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('admin-reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin-reviews/delete/<int:pk>/', views.delete_review, name='delete_review'),

    # My Account Sub-Pages
    path('compare-history/', views.compare_history, name='compare_history'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/toggle/<int:car_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('recently-viewed/', views.recently_viewed_page, name='recently_viewed'),
    path('track-view/<int:car_id>/', views.track_view, name='track_view'),
    path('accessories/', views.suggested_accessories, name='suggested_accessories'),
    path('accessories/toggle/<int:pk>/', views.toggle_favorite_accessory, name='toggle_favorite_accessory'),
    path('documents/', views.documents_reminders, name='documents_reminders'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/delete/<int:pk>/', views.delete_document, name='delete_document'),
    path('reminders/add/', views.add_reminder, name='add_reminder'),
    path('reminders/delete/<int:pk>/', views.delete_reminder, name='delete_reminder'),
    path('settings/', views.user_settings, name='user_settings'),
]


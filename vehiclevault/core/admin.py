from django.contrib import admin
from .models import User, AdminSignupRequest


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_superuser', 'created_at']
    list_filter = ['role', 'is_active', 'is_superuser']
    search_fields = ['email', 'first_name', 'last_name']


@admin.register(AdminSignupRequest)
class AdminSignupRequestAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'status', 'requested_at', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['requested_at', 'reviewed_at']

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .models import Car, FavoriteVehicle, CompareHistory, UserDocument, Reminder, Accessory, AdminNotification
from .forms import CarForm, UserDocumentForm, ReminderForm, AccessoryForm, AdminNotificationForm
from django.contrib import messages

# Create your views here.
@role_required(allowed_roles=["admin"]) 
def adminDashboardView(request):
    cars_count = Car.objects.count()
    return render(request, "vehicles/admin/admin_dashboard.html", {'cars_count': cars_count})

@role_required(allowed_roles=["user"]) 
def userDashboardView(request):
    documents_count = UserDocument.objects.filter(user=request.user).count()
    reminders_count = Reminder.objects.filter(user=request.user).count()
    context = {
        'documents_count': documents_count,
        'reminders_count': reminders_count
    }
    return render(request, "vehicles/user/user_dashboard.html", context)

# --- Admin Views Example ---
@role_required(allowed_roles=["admin"])
def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car added successfully!')
            return redirect('admin_dashboard')  # Update with your actual URL name
    else:
        form = CarForm()
    
    # Needs a template 'vehicles/admin/add_car.html' to render the form
    return render(request, 'vehicles/admin/add_car.html', {'form': form})

# --- User Views Example ---
@role_required(allowed_roles=["user"])
def add_document(request):
    if request.method == 'POST':
        form = UserDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user  # Assign current logged-in user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('user_dashboard')  # Update with your actual URL name
    else:
        form = UserDocumentForm()
    
    # Needs a template 'vehicles/user/add_document.html' to render the form
    return render(request, 'vehicles/user/add_document.html', {'form': form})

@role_required(allowed_roles=["user"])
def add_reminder(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user  # Assign current logged-in user
            reminder.save()
            messages.success(request, 'Reminder added successfully!')
            return redirect('user_dashboard')  # Update with your actual URL name
    else:
        form = ReminderForm()
        
    # Needs a template 'vehicles/user/add_reminder.html' to render the form
    return render(request, 'vehicles/user/add_reminder.html', {'form': form})
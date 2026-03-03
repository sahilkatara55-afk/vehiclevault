from django.shortcuts import render, redirect, get_object_or_404
from .forms import UsersignupForm, UserProfileUpdateForm, OTPVerifyForm
from .models import User, AdminSignupRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
import random


# Helper: generate 6-digit OTP
def _generate_otp():
    return str(random.randint(100000, 999999))



# Signup View — Step 1: collect details, send OTP
def Usersignupview(request):

    if request.method == 'POST':

        form = UsersignupForm(request.POST)

        if form.is_valid():
            email      = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name  = form.cleaned_data['last_name']
            gender     = form.cleaned_data.get('gender') or None
            password   = form.cleaned_data['password1']
            role       = form.cleaned_data.get('role', 'user')

            # Generate OTP and store everything in session
            otp = _generate_otp()

            request.session['pending_signup'] = {
                'email':      email,
                'first_name': first_name,
                'last_name':  last_name,
                'gender':     gender,
                'password':   password,   # raw — used only until OTP verified
                'role':       role,
                'otp':        otp,
                'otp_created': timezone.now().isoformat(),
            }

            # Send OTP email
            send_mail(
                subject='VehicleVault — Your OTP Code',
                message=(
                    f'Hi {first_name},\n\n'
                    f'Your OTP for VehicleVault signup is:\n\n'
                    f'   {otp}\n\n'
                    f'This OTP is valid for 10 minutes. Do not share it with anyone.\n\n'
                    f'— VehicleVault Team'
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('verify_otp')

        else:
            return render(request, 'core/signup.html', {'form': form})

    else:
        form = UsersignupForm()
        return render(request, 'core/signup.html', {'form': form})


# ──────────────────────────────────────────────
# OTP Verify View — Step 2: verify OTP & create account
# ──────────────────────────────────────────────
def verify_otp(request):
    pending = request.session.get('pending_signup')

    if not pending:
        messages.error(request, 'Session expired. Please signup again.')
        return redirect('signup')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)

        if form.is_valid():
            entered_otp = form.cleaned_data['otp']

            # OTP expiry check (10 minutes)
            from datetime import datetime, timedelta
            otp_created = datetime.fromisoformat(pending['otp_created'])
            # Make timezone-aware comparison
            now_utc = timezone.now()
            if timezone.is_naive(otp_created):
                from django.utils.timezone import make_aware
                otp_created = make_aware(otp_created)
            if now_utc - otp_created > timedelta(minutes=10):
                del request.session['pending_signup']
                messages.error(request, 'OTP has expired. Please signup again.')
                return redirect('signup')

            if entered_otp != pending['otp']:
                form.add_error('otp', 'Invalid OTP. Please try again.')
                return render(request, 'core/verify_otp.html', {
                    'form': form,
                    'email': pending['email'],
                })

            # OTP is correct — create account
            email      = pending['email']
            first_name = pending['first_name']
            last_name  = pending['last_name']
            gender     = pending['gender']
            password   = pending['password']
            role       = pending['role']

            del request.session['pending_signup']

            if role == 'admin':
                AdminSignupRequest.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    email=email,
                    password=make_password(password),
                    status='pending'
                )
                send_mail(
                    subject='VehicleVault — Admin Request Received',
                    message=(
                        f'Hi {first_name},\n\n'
                        'Your request for admin access has been received and is pending approval.\n'
                        'You will be notified once a superadmin reviews your request.\n\n'
                        '— VehicleVault Team'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=True,
                )
                messages.success(
                    request,
                    'Email verified! Your admin access request is pending approval.'
                )
                return redirect('admin_request_pending')

            else:
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    role='user',
                )
                user.set_password(password)
                user.save()

                send_mail(
                    subject='VehicleVault — Welcome!',
                    message=f'Hi {first_name}, your account has been created successfully. Welcome to VehicleVault!',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=True,
                )
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('login')

        return render(request, 'core/verify_otp.html', {
            'form': form,
            'email': pending['email'],
        })

    else:
        form = OTPVerifyForm()
        return render(request, 'core/verify_otp.html', {
            'form': form,
            'email': pending['email'],
        })


# ──────────────────────────────────────────────
# Resend OTP
# ──────────────────────────────────────────────
def resend_otp(request):
    pending = request.session.get('pending_signup')

    if not pending:
        messages.error(request, 'Session expired. Please signup again.')
        return redirect('signup')

    otp = _generate_otp()
    pending['otp'] = otp
    pending['otp_created'] = timezone.now().isoformat()
    request.session['pending_signup'] = pending
    request.session.modified = True

    send_mail(
        subject='VehicleVault — New OTP Code',
        message=(
            f'Hi {pending["first_name"]},\n\n'
            f'Your new OTP for VehicleVault signup is:\n\n'
            f'   {otp}\n\n'
            f'This OTP is valid for 10 minutes.\n\n'
            f'— VehicleVault Team'
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[pending['email']],
        fail_silently=True,
    )

    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('verify_otp')


# ──────────────────────────────────────────────
# Admin Request Pending Page
# ──────────────────────────────────────────────
def admin_request_pending(request):
    return render(request, 'core/admin_request_pending.html')


# ──────────────────────────────────────────────
# Admin: Pending Requests List  (superuser only)
# ──────────────────────────────────────────────
@login_required
def admin_requests_list(request):
    if not request.user.is_superuser:
        return redirect('user_dashboard')

    status_filter = request.GET.get('status', 'pending')
    requests_qs = AdminSignupRequest.objects.filter(status=status_filter)
    pending_count = AdminSignupRequest.objects.filter(status='pending').count()

    return render(request, 'core/admin_requests.html', {
        'requests': requests_qs,
        'status_filter': status_filter,
        'pending_count': pending_count,
    })


# ──────────────────────────────────────────────
# Admin: Approve Request
# ──────────────────────────────────────────────
@login_required
def approve_admin_request(request, pk):
    if not request.user.is_superuser:
        return redirect('user_dashboard')

    admin_req = get_object_or_404(AdminSignupRequest, pk=pk, status='pending')

    user = User(
        email=admin_req.email,
        first_name=admin_req.first_name,
        last_name=admin_req.last_name,
        gender=admin_req.gender,
        role='admin',
        is_staff=True,
        is_admin=True,
        is_active=True,
    )
    user.password = admin_req.password
    user.save()

    admin_req.status = 'approved'
    admin_req.reviewed_at = timezone.now()
    admin_req.save()

    send_mail(
        subject='VehicleVault — Admin Access Approved!',
        message=(
            f'Hi {admin_req.first_name},\n\n'
            'Congratulations! Your admin access request has been approved.\n'
            'You can now login to VehicleVault with your email and password.\n\n'
            '— VehicleVault Team'
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[admin_req.email],
        fail_silently=True,
    )

    messages.success(request, f'Admin access approved for {admin_req.email}.')
    return redirect('admin_requests_list')


# ──────────────────────────────────────────────
# Admin: Reject Request
# ──────────────────────────────────────────────
@login_required
def reject_admin_request(request, pk):
    if not request.user.is_superuser:
        return redirect('user_dashboard')

    admin_req = get_object_or_404(AdminSignupRequest, pk=pk, status='pending')
    admin_req.status = 'rejected'
    admin_req.reviewed_at = timezone.now()
    admin_req.save()

    send_mail(
        subject='VehicleVault — Admin Access Request Update',
        message=(
            f'Hi {admin_req.first_name},\n\n'
            'Unfortunately, your admin access request has not been approved at this time.\n'
            'You can still signup as a regular user.\n\n'
            '— VehicleVault Team'
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[admin_req.email],
        fail_silently=True,
    )

    messages.info(request, f'Admin request rejected for {admin_req.email}.')
    return redirect('admin_requests_list')


# ──────────────────────────────────────────────
# Home
# ──────────────────────────────────────────────
def home(request):
    return render(request, 'home.html')


# ──────────────────────────────────────────────
# Login View
# ──────────────────────────────────────────────
def userloginform(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            return render(request, 'core/login.html', {
                'error': 'Invalid Email or Password'
            })

    return render(request, 'core/login.html')


# ──────────────────────────────────────────────
# User Dashboard
# ──────────────────────────────────────────────
@login_required
def user_dashboard(request):
    return render(request, 'vehicles/user/user_dashboard.html')


# ──────────────────────────────────────────────
# My Account Page
# ──────────────────────────────────────────────
@login_required
def my_account(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('my_account')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'core/my_account.html', {'form': form})


# ──────────────────────────────────────────────
# Admin Dashboard
# ──────────────────────────────────────────────
@login_required
def admin_dashboard(request):
    pending_count = AdminSignupRequest.objects.filter(status='pending').count()
    return render(request, 'vehicles/admin/admin_dashboard.html', {
        'pending_count': pending_count,
    })


# ──────────────────────────────────────────────
# Logout View
# ──────────────────────────────────────────────
def logout_user(request):
    logout(request)
    return redirect('login')
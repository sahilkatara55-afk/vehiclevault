from django.shortcuts import render, redirect, get_object_or_404
from .forms import UsersignupForm, UserProfileUpdateForm, OTPVerifyForm
from .models import User, AdminSignupRequest
from vehicles.models import Car, FavoriteVehicle, CompareHistory, RecentlyViewed, UserDocument, Reminder, Accessory, AdminNotification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
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
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    from django.db.models import Count
    pending_count = AdminSignupRequest.objects.filter(status='pending').count()
    total_cars    = Car.objects.count()
    total_users   = User.objects.filter(is_superuser=False, is_deleted=False).count()
    total_comparisons = CompareHistory.objects.count()
    total_accessories = Accessory.objects.count()
    top_compared = (
        Car.objects.annotate(cmp_count=Count('compared_in'))
        .order_by('-cmp_count')[:5]
    )
    return render(request, 'vehicles/admin/admin_dashboard.html', {
        'pending_count':      pending_count,
        'total_cars':         total_cars,
        'total_users':        total_users,
        'total_comparisons':  total_comparisons,
        'total_accessories':  total_accessories,
        'top_compared':       top_compared,
    })


# ──────────────────────────────────────────────
# Admin Sidebar Placeholder Views
# ──────────────────────────────────────────────
# ──────────────────────────────────────────────
# Car Management
# ──────────────────────────────────────────────
@login_required
def manage_cars(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    cars = Car.objects.all()
    return render(request, 'vehicles/admin/manage_cars.html', {'cars': cars})


@login_required
def car_add(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    if request.method == 'POST':
        car = Car(
            make=request.POST['make'],
            model=request.POST['model'],
            year=request.POST['year'],
            price=request.POST['price'],
            mileage=request.POST.get('mileage', ''),
            engine=request.POST['engine'],
            transmission=request.POST.get('transmission', 'manual'),
            description=request.POST.get('description', ''),
            safety_rating=request.POST['safety_rating'],
        )
        if 'image' in request.FILES:
            car.image = request.FILES['image']
        car.save()
        messages.success(request, f'{car} added successfully.')
    return redirect('manage_cars')


@login_required
def car_edit(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.make         = request.POST['make']
        car.model        = request.POST['model']
        car.year         = request.POST['year']
        car.price        = request.POST['price']
        car.mileage      = request.POST.get('mileage', '')
        car.engine       = request.POST['engine']
        car.transmission = request.POST.get('transmission', 'manual')
        car.description  = request.POST.get('description', '')
        car.safety_rating = request.POST['safety_rating']
        if 'image' in request.FILES:
            car.image = request.FILES['image']
        car.save()
        messages.success(request, f'{car} updated successfully.')
    return redirect('manage_cars')


@login_required
def car_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    car = get_object_or_404(Car, pk=pk)
    car.delete()
    messages.success(request, 'Car deleted successfully.')
    return redirect('manage_cars')


# ──────────────────────────────────────────────
# User Management
# ──────────────────────────────────────────────
@login_required
def manage_users(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    q = request.GET.get('q', '').strip()
    users = User.objects.filter(is_superuser=False, is_deleted=False)
    if q:
        users = users.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)  |
            Q(email__icontains=q)
        )
    return render(request, 'vehicles/admin/manage_users.html', {'users': users, 'q': q})


@login_required
def user_toggle_block(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'Unblocked' if user.is_active else 'Blocked'
    messages.success(request, f'User {user.email} {status}.')
    return redirect('manage_users')


@login_required
def user_delete_admin(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    user = get_object_or_404(User, pk=pk)
    user.is_deleted = True
    user.deleted_at  = timezone.now()
    user.is_active   = False
    user.save()
    messages.success(request, f'User {user.email} deleted.')
    return redirect('manage_users')


@login_required
def manage_accessories(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    accessories = Accessory.objects.all()
    return render(request, 'vehicles/admin/manage_accessories.html', {'accessories': accessories})


@login_required
def accessory_add(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    if request.method == 'POST':
        acc = Accessory(
            name=request.POST['name'],
            compatible_car=request.POST.get('compatible_car', ''),
            price=request.POST['price'],
            description=request.POST.get('description', ''),
        )
        if 'image' in request.FILES:
            acc.image = request.FILES['image']
        acc.save()
        messages.success(request, f'Accessory "{acc.name}" added.')
    return redirect('manage_accessories')


@login_required
def accessory_edit(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    acc = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        acc.name           = request.POST['name']
        acc.compatible_car = request.POST.get('compatible_car', '')
        acc.price          = request.POST['price']
        acc.description    = request.POST.get('description', '')
        if 'image' in request.FILES:
            acc.image = request.FILES['image']
        acc.save()
        messages.success(request, f'Accessory "{acc.name}" updated.')
    return redirect('manage_accessories')


@login_required
def accessory_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    acc = get_object_or_404(Accessory, pk=pk)
    acc.delete()
    messages.success(request, 'Accessory deleted.')
    return redirect('manage_accessories')


@login_required
def admin_notifications(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        message_txt = request.POST.get('message', '').strip()
        send_to_all = request.POST.get('send_to_all', '1') == '1'
        if title and message_txt:
            notif = AdminNotification.objects.create(
                title=title,
                message=message_txt,
                sent_to_all=send_to_all,
            )
            if not send_to_all:
                selected_ids = request.POST.getlist('user_ids')
                notif.recipients.set(User.objects.filter(pk__in=selected_ids))
            messages.success(request, f'Notification "{title}" sent.')
        else:
            messages.error(request, 'Title and message are required.')
        return redirect('admin_notifications')
    notifications = AdminNotification.objects.all()
    all_users     = User.objects.filter(is_superuser=False, is_deleted=False)
    return render(request, 'vehicles/admin/admin_notifications.html', {
        'notifications': notifications,
        'all_users':     all_users,
    })


@login_required
def admin_reports(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    from django.db.models import Count
    report_data = (
        Car.objects.annotate(cmp_count=Count('compared_in'))
        .order_by('-cmp_count')
    )
    total_comparisons = CompareHistory.objects.count()
    total_cars        = Car.objects.count()
    total_users       = User.objects.filter(is_superuser=False, is_deleted=False).count()
    return render(request, 'vehicles/admin/admin_reports.html', {
        'report_data':       report_data,
        'total_comparisons': total_comparisons,
        'total_cars':        total_cars,
        'total_users':       total_users,
    })


@login_required
def admin_settings(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_dashboard')
    from django.contrib.auth.hashers import check_password as _check
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'profile':
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name  = request.POST.get('last_name', request.user.last_name)
            if 'profile_picture' in request.FILES:
                request.user.profile_picture = request.FILES['profile_picture']
            request.user.save()
            messages.success(request, 'Profile updated.')
        elif action == 'password':
            old_pw  = request.POST.get('old_password', '')
            new_pw  = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')
            if not _check(old_pw, request.user.password):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                messages.success(request, 'Password changed. Please log in again.')
                return redirect('login')
    return render(request, 'vehicles/admin/admin_settings.html')


# ──────────────────────────────────────────────
# Logout View
# ──────────────────────────────────────────────
def logout_user(request):
    logout(request)
    return redirect('login')


# ──────────────────────────────────────────────
# Search Cars
# ──────────────────────────────────────────────
def search_cars(request):
    cars = Car.objects.all()
    brands = Car.objects.values_list('make', flat=True).distinct().order_by('make')

    # Filter fields
    brand       = request.GET.get('brand', '').strip()
    fuel        = request.GET.get('fuel', '').strip()
    transmission = request.GET.get('transmission', '').strip()
    price_min   = request.GET.get('price_min', '').strip()
    price_max   = request.GET.get('price_max', '').strip()
    query       = request.GET.get('q', '').strip()

    if query:
        cars = cars.filter(
            Q(make__icontains=query) | Q(model__icontains=query)
        )
    if brand:
        cars = cars.filter(make__iexact=brand)
    if fuel:
        cars = cars.filter(engine=fuel)
    if transmission:
        cars = cars.filter(transmission=transmission)
    if price_min:
        try:
            cars = cars.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            cars = cars.filter(price__lte=float(price_max))
        except ValueError:
            pass

    fav_ids = set()
    if request.user.is_authenticated:
        fav_ids = set(FavoriteVehicle.objects.filter(user=request.user).values_list('car_id', flat=True))

    return render(request, 'vehicles/search_cars.html', {
        'cars': cars,
        'brands': brands,
        'selected_brand': brand,
        'selected_fuel': fuel,
        'selected_transmission': transmission,
        'price_min': price_min,
        'price_max': price_max,
        'query': query,
        'total': cars.count(),
        'fav_ids': fav_ids,
    })


# ──────────────────────────────────────────────
# Brands
# ──────────────────────────────────────────────
def brands_view(request):
    from django.db.models import Count
    brands_data = (
        Car.objects.values('make')
        .annotate(car_count=Count('id'))
        .order_by('make')
    )
    return render(request, 'vehicles/brands.html', {'brands_data': brands_data})


def brand_cars(request, make):
    cars = Car.objects.filter(make__iexact=make).order_by('-year')
    return render(request, 'vehicles/brand_cars.html', {
        'cars': cars,
        'brand_name': make,
        'total': cars.count(),
    })


# ──────────────────────────────────────────────
# Compare Cars
# ──────────────────────────────────────────────
def compare_cars(request):
    all_cars = Car.objects.all().order_by('make', 'model')

    selected_ids_raw = request.GET.get('ids', '')
    selected_ids = [int(i) for i in selected_ids_raw.split(',') if i.strip().isdigit()][:3]
    compare_list = []
    if selected_ids:
        compare_list = list(Car.objects.filter(id__in=selected_ids))

    return render(request, 'vehicles/compare_cars.html', {
        'all_cars': all_cars,
        'compare_list': compare_list,
        'selected_ids': selected_ids,
        'selected_ids_str': ','.join(str(i) for i in selected_ids),
    })

# ──────────────────────────────────────────────
# Compare History
# ──────────────────────────────────────────────
@login_required
def compare_history(request):
    history = CompareHistory.objects.filter(user=request.user).prefetch_related('cars')
    return render(request, 'vehicles/user/compare_history.html', {'history': history})


# ──────────────────────────────────────────────
# Favorite Vehicles
# ──────────────────────────────────────────────
@login_required
def favorites(request):
    fav_list = FavoriteVehicle.objects.filter(user=request.user).select_related('car')
    return render(request, 'vehicles/user/favorites.html', {'fav_list': fav_list})


@login_required
def toggle_favorite(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    fav, created = FavoriteVehicle.objects.get_or_create(user=request.user, car=car)
    if not created:
        fav.delete()
        messages.info(request, f'{car} removed from favorites.')
    else:
        messages.success(request, f'{car} added to favorites!')
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/favorites/'))
    return redirect(next_url)


# ──────────────────────────────────────────────
# Recently Viewed
# ──────────────────────────────────────────────
@login_required
def recently_viewed_page(request):
    viewed = RecentlyViewed.objects.filter(user=request.user).select_related('car')[:10]
    return render(request, 'vehicles/user/recently_viewed.html', {'viewed': viewed})


@login_required
def track_view(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    RecentlyViewed.objects.update_or_create(user=request.user, car=car)
    return redirect('compare_cars')


# ──────────────────────────────────────────────
# Suggested Accessories
# ──────────────────────────────────────────────
@login_required
def suggested_accessories(request):
    fav_makes    = list(FavoriteVehicle.objects.filter(user=request.user).values_list('car__make', flat=True))
    viewed_makes = list(RecentlyViewed.objects.filter(user=request.user).values_list('car__make', flat=True))
    all_makes    = list(set(fav_makes + viewed_makes))
    fav_car_ids  = FavoriteVehicle.objects.filter(user=request.user).values_list('car_id', flat=True)
    suggested    = Car.objects.filter(make__in=all_makes).exclude(id__in=fav_car_ids)[:6] if all_makes else Car.objects.all()[:6]
    return render(request, 'vehicles/user/suggested_accessories.html', {'suggested': suggested, 'all_makes': all_makes})


# ──────────────────────────────────────────────
# Documents & Reminders
# ──────────────────────────────────────────────
@login_required
def documents_reminders(request):
    docs      = UserDocument.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user)
    return render(request, 'vehicles/user/documents_reminders.html', {'docs': docs, 'reminders': reminders})


@login_required
def upload_document(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        file  = request.FILES.get('file')
        if title and file:
            UserDocument.objects.create(user=request.user, title=title, file=file)
            messages.success(request, 'Document uploaded.')
        else:
            messages.error(request, 'Provide title and file.')
    return redirect('documents_reminders')


@login_required
def delete_document(request, pk):
    doc = get_object_or_404(UserDocument, pk=pk, user=request.user)
    doc.file.delete(save=False)
    doc.delete()
    messages.success(request, 'Document deleted.')
    return redirect('documents_reminders')


@login_required
def add_reminder(request):
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        r_type   = request.POST.get('type', 'other')
        due_date = request.POST.get('due_date', '')
        notes    = request.POST.get('notes', '')
        if title and due_date:
            Reminder.objects.create(user=request.user, title=title, type=r_type, due_date=due_date, notes=notes)
            messages.success(request, 'Reminder added.')
        else:
            messages.error(request, 'Title and due date are required.')
    return redirect('documents_reminders')


@login_required
def delete_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    reminder.delete()
    messages.success(request, 'Reminder deleted.')
    return redirect('documents_reminders')


# ──────────────────────────────────────────────
# User Settings
# ──────────────────────────────────────────────
@login_required
def user_settings(request):
    from django.contrib.auth.hashers import check_password as _check
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'profile':
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name  = request.POST.get('last_name', request.user.last_name)
            if 'profile_picture' in request.FILES:
                request.user.profile_picture = request.FILES['profile_picture']
            request.user.save()
            messages.success(request, 'Profile updated.')
        elif action == 'password':
            old_pw  = request.POST.get('old_password', '')
            new_pw  = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')
            if not _check(old_pw, request.user.password):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                messages.success(request, 'Password changed. Please log in again.')
                logout(request)
                return redirect('login')
    return render(request, 'vehicles/user/user_settings.html')

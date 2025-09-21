from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User, Ride, RideRequest, DriverVerification, Notification, Payment


# Helper functions for user roles
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def is_driver(user):
    return user.is_authenticated and user.role == 'driver'


def is_rider(user):
    return user.is_authenticated and user.role == 'passenger'  # Adjust if needed


# Authentication Views
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"Login attempt email={email}")

        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            username = user_qs.first().username
        else:
            username = email

        user = authenticate(request, username=username, password=password)

        if user:
            print(f"User {user.username} authenticated successfully.")
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'driver':
                return redirect('driver_dashboard')
            else:
                return redirect('rider_dashboard')
        else:
            print("Authentication failed")
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        role = request.POST.get('role', 'passenger')

        if not (username and email and password):
            messages.error(request, 'All fields are required.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            user.save()
            login(request, user)
            return redirect('rider_dashboard')
    return render(request, 'register.html')


# Dashboard Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.exclude(role='admin')
    rides = Ride.objects.all()
    verifications = DriverVerification.objects.all()
    payments = Payment.objects.all()
    if request.method == 'POST':
        if 'block_user' in request.POST:
            user = User.objects.get(pk=request.POST['user_id'])
            user.blocked = True
            user.save()
            messages.success(request, 'User blocked.')
        elif 'unblock_user' in request.POST:
            user = User.objects.get(pk=request.POST['user_id'])
            user.blocked = False
            user.save()
            messages.success(request, 'User unblocked.')
    return render(request, 'admin_dashboard.html', {
        'users': users, 'rides': rides, 'verifications': verifications, 'payments': payments
    })


@login_required
@user_passes_test(is_driver)
def driver_dashboard(request):
    my_rides = Ride.objects.filter(user=request.user)
    ride_requests = RideRequest.objects.filter(ride__user=request.user)
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'driver_dashboard.html', {
        'my_rides': my_rides, 'ride_requests': ride_requests, 'notifications': notifications
    })


@login_required
@user_passes_test(is_rider)
def rider_dashboard(request):
    joined_rides = RideRequest.objects.filter(passenger=request.user)
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'rider_dashboard.html', {
        'joined_rides': joined_rides, 'notifications': notifications
    })


# Hiring Driver View
@login_required
def hire_driver(request):
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        date = request.POST.get('date')
        # Add any other fields needed as per model
        RideRequest.objects.create(
            passenger=request.user,
            status="pending"
        )
        messages.success(request, 'Driver hire request submitted.')
        return redirect('rider_dashboard')
    return render(request, 'hire_driver.html')


# Management Views for Admin
@login_required
@user_passes_test(is_admin)
def manage_hire_requests(request):
    requests = RideRequest.objects.filter(status='pending')
    if request.method == 'POST':
        # Implement handling driver assignment, statuses, notifications as needed
        pass
    return render(request, 'manage_hire_requests.html', {'requests': requests})


@login_required
@user_passes_test(is_admin)
def manage_rides(request):
    rides = Ride.objects.all()
    if request.method == 'POST':
        # Implement approve/delete/modify rides as needed
        pass
    return render(request, 'manage_rides.html', {'rides': rides})


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.exclude(role='admin')
    if request.method == 'POST':
        # Implement approve/reject/block/unblock/delete user operations
        pass
    return render(request, 'manage_users.html', {'users': users})


# Notifications
@login_required
def notifications(request):
    notes = Notification.objects.filter(user=request.user)
    if request.method == 'POST':
        # Implement mark read or delete functionality
        pass
    return render(request, 'notifications.html', {'notifications': notes})


# Driver posts ride
@login_required
@user_passes_test(is_driver)
def post_ride(request):
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        date = request.POST.get('date')
        seats = request.POST.get('seats')
        price = request.POST.get('price')
        Ride.objects.create(
            user=request.user,
            origin=origin,
            destination=destination,
            ridedate=date,
            seats=seats,
            price=price
        )
        messages.success(request, "Ride posted successfully!")
        return redirect('driver_dashboard')
    return render(request, 'post_ride.html')


# Process payment view
@login_required
def process_payment(request):
    if request.method == 'POST':
        # Handle payment processing logic here
        messages.success(request, "Payment processed!")
        return redirect('profile')
    return render(request, 'process_payment.html')


# User profile view
@login_required
def profile(request):
    if request.method == 'POST':
        # Process profile update fields and uploads
        messages.success(request, "Profile updated.")
        return redirect('profile')
    return render(request, 'profile.html', {'user': request.user})


# Rate driver view
@login_required
def rate_driver(request):
    if request.method == 'POST':
        # Process rating and comment submission
        messages.success(request, "Driver rated.")
        return redirect('rider_dashboard')
    return render(request, 'rate_driver.html')


# Ride search and request join
@login_required
def search_ride(request):
    rides = []
    if request.method == 'GET':
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        if origin and destination:
            rides = Ride.objects.filter(origin__icontains=origin, destination__icontains=destination, status='available')
    if request.method == 'POST':
        ride_id = request.POST.get('ride_id')
        ride = get_object_or_404(Ride, id=ride_id)
        RideRequest.objects.create(ride=ride, passenger=request.user, status='pending')
        messages.success(request, "Ride request sent!")
        return redirect('rider_dashboard')
    return render(request, 'search_ride.html', {'rides': rides})

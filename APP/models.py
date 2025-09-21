from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    ROLE_CHOICES = [
        ('passenger', 'Passenger'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='passenger')
    preferences = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='other')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')
    verified = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    vehicletype = models.CharField(max_length=50, blank=True)
    vehicleregnumber = models.CharField(max_length=20, blank=True)
    govidurl = models.CharField(max_length=255, blank=True)  # Government ID URL
    vehicledetails = models.TextField(blank=True)
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Ride(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    RIDETYPE_CHOICES = [
        ('solo', 'Solo'),
        ('shared', 'Shared'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_rides')
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    ridedate = models.DateField()
    seats = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    ridetype = models.CharField(max_length=10, choices=RIDETYPE_CHOICES, default='shared')
    originlat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    originlon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destlat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destlon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin} to {self.destination} on {self.ridedate}"

    class Meta:
        ordering = ['-createdat']


class RideRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
        ('cancelled', 'Cancelled'),
    ]

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='requests')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ride_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requestedseats = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    createdat = models.DateTimeField(auto_now_add=True)
    acceptedat = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.passenger.username} -> {self.ride}"

    class Meta:
        unique_together = ('ride', 'passenger')
        ordering = ['-createdat']


class Traveller(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    request = models.ForeignKey(RideRequest, on_delete=models.CASCADE, related_name='travellers')
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.gender})"


class DriverVerification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    licenseurl = models.CharField(max_length=255, blank=True)
    rcurl = models.CharField(max_length=255, blank=True)  # Registration Certificate URL
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.user.username}"


class TripHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_history')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='trip_history')
    tripdate = models.DateField()
    distance = models.PositiveIntegerField(help_text="Distance in kilometers")
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ride} on {self.tripdate}"

    class Meta:
        ordering = ['-tripdate']
        verbose_name_plural = "Trip histories"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    isread = models.BooleanField(default=False)
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."

    class Meta:
        ordering = ['-createdat']


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='payments')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paymentmethod = models.CharField(max_length=50, blank=True)
    transactionid = models.CharField(max_length=100, blank=True, unique=True)
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of ${self.amount} by {self.passenger.username}"

    class Meta:
        ordering = ['-createdat']


class HireRequest(models.Model):
    """Model for hiring a driver for a specific trip"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Driver Assigned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hire_requests')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_hires')
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    pickupdate = models.DateField()
    pickuptime = models.TimeField()
    passengers = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    estimatedfare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hire request: {self.origin} to {self.destination} on {self.pickupdate}"

    class Meta:
        ordering = ['-createdat']

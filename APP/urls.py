from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('driver-dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('rider-dashboard/', views.rider_dashboard, name='rider_dashboard'),
    path('hire-driver/', views.hire_driver, name='hire_driver'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('manage-hire-requests/', views.manage_hire_requests, name='manage_hire_requests'),
    path('manage-rides/', views.manage_rides, name='manage_rides'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('notifications/', views.notifications, name='notifications'),
    path('post-ride/', views.post_ride, name='post_ride'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('profile/', views.profile, name='profile'),
    path('rate-driver/', views.rate_driver, name='rate_driver'),
    path('register/', views.register, name='register'),
    path('search-ride/', views.search_ride, name='search_ride'),
]

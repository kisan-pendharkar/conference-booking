# bookings/urls.py - Updated with logout fix
from django.urls import path
from . import views

urlpatterns = [
    # Home and main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Conference-related URLs
    path('conference/<int:pk>/', views.conference_detail, name='conference_detail'),
    path('book/<int:pk>/', views.book_conference, name='book_conference'),
    path('conference/add/', views.add_conference, name='add_conference'),
    path('location/add/', views.add_location, name='add_location'),
    path('conference/<int:pk>/edit/', views.edit_conference, name='edit_conference'),
    path('conference/<int:pk>/delete/', views.delete_conference, name='delete_conference'),
    
    # Booking management
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:pk>/', views.cancel_booking, name='cancel_booking'),
    
    # Manager/Admin URLs
    path('manage-bookings/', views.manage_bookings, name='manage_bookings'),
    path('approve-booking/<int:pk>/', views.approve_booking, name='approve_booking'),
    
    # Reports and exports
    path('reports/', views.reports, name='reports'),
    path('export-bookings/', views.export_bookings, name='export_bookings'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),  # Custom logout view
    
    # API endpoints (optional)
    path('api/conference/<int:pk>/availability/', views.api_conference_availability, name='api_conference_availability'),
]
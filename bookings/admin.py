from django.contrib import admin
from .models import Conference, Booking

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'venue', 'capacity', 'price']
    list_filter = ['date', 'venue']
    search_fields = ['title', 'venue']
    ordering = ['-date']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'conference', 'booking_date', 'status']
    list_filter = ['status', 'booking_date', 'conference']
    search_fields = ['user__username', 'conference__title']
    ordering = ['-booking_date']
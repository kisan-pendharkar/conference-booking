# bookings/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Location model
class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ConferenceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Conference Categories"
    
    def __str__(self):
        return self.name

class Conference(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    capacity = models.PositiveIntegerField()
    requires_approval = models.BooleanField(default=True)
    image = models.ImageField(upload_to='conferences/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('conference_detail', args=[str(self.id)])
    
    def available_seats(self):
        """Calculate available seats"""
        booked = Booking.objects.filter(
            conference=self, 
            status__in=['pending', 'approved']
        ).count()
        return self.capacity - booked
    
    # def total_cost(self):
    #     """Calculate total cost of approved bookings"""
    #     return Booking.objects.filter(
    #         conference=self, 
    #         status='approved'
    #     ).count() * self.price

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    justification = models.TextField(
        help_text="Please explain why you need to attend this conference",
        blank=True
    )
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_bookings'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('user', 'conference')
    
    def __str__(self):
        return f"{self.user.username} - {self.conference.title}"
    
    def get_status_display_color(self):
        """Return CSS color class for status"""
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
        }
        return status_colors.get(self.status, 'secondary')
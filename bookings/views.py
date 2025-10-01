# Manager/Admin views

# bookings/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import csv
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from .models import Conference, Booking, ConferenceCategory, Location


def is_admin(user):
    """Check if user is admin only"""
    return (hasattr(user, 'is_admin') and user.is_admin()) or user.is_superuser

# Location Form
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address']

# Add Location
@login_required
@user_passes_test(is_admin)
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location added successfully.')
            return redirect('add_conference')
    else:
        form = LocationForm()
    return render(request, 'bookings/location_form.html', {'form': form})


# Manager/Admin views
def is_admin(user):
    """Check if user is admin only"""
    return (hasattr(user, 'is_admin') and user.is_admin()) or user.is_superuser

# Conference Form
class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ['title', 'description', 'location' , 'capacity', 'requires_approval', 'image']

# Add Conference    
@login_required
@user_passes_test(is_admin)
def add_conference(request):
    locations = Location.objects.all()
    if request.method == 'POST':
        form = ConferenceForm(request.POST, request.FILES)
        if form.is_valid():
            conference = form.save(commit=False)
            conference.created_by = request.user
            conference.save()
            messages.success(request, 'Conference added successfully.')
            return redirect('conference_detail', pk=conference.pk)
    else:
        form = ConferenceForm()
    return render(request, 'bookings/conference_form.html', {'form': form, 'action': 'Add', 'locations': locations})

# Edit Conference
@login_required
@user_passes_test(is_admin)
def edit_conference(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    if request.method == 'POST':
        form = ConferenceForm(request.POST, request.FILES, instance=conference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conference updated successfully.')
            return redirect('conference_detail', pk=conference.pk)
    else:
        form = ConferenceForm(instance=conference)
    return render(request, 'bookings/conference_form.html', {'form': form, 'action': 'Edit'})

# Delete Conference
@login_required
@user_passes_test(is_admin)
def delete_conference(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    if request.method == 'POST':
        conference.delete()
        messages.success(request, 'Conference deleted successfully.')
        return redirect('home')
    return render(request, 'bookings/conference_confirm_delete.html', {'conference': conference})

def home(request):
    """Home page view with conference listings"""
    # Get all categories for filtering
    categories = ConferenceCategory.objects.all()
    
    # Get upcoming conferences
    conferences = Conference.objects.order_by('created_at')

    # Search functionality
    search_query = request.GET.get('search')
    category_filter = request.GET.get('category')

    if search_query:
        conferences = conferences.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(venue__icontains=search_query)
        )

    if category_filter:
        conferences = conferences.filter(category_id=category_filter)

    # Group conferences by location
    locations = Location.objects.all()
    conferences_by_location = {}
    for location in locations:
        conferences_by_location[location] = conferences.filter(location=location)

    context = {
        'conferences_by_location': conferences_by_location,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'locations': locations,
    }
    return render(request, 'bookings/home.html', context)

@login_required
def dashboard(request):
    """User dashboard with personal statistics"""
    # Get user's recent bookings
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')[:5]
    
    # Get upcoming conferences
    upcoming_conferences = Conference.objects.order_by('created_at')[:5]

    # Calculate statistics
    total_conferences = Conference.objects.count()
    booked_conferences = Booking.objects.filter(user=request.user).count()
    available_conferences = Conference.objects.filter(created_at__gte=timezone.now().date()).count()
    stats = {
        'total_conferences': total_conferences,
        'booked_conferences': booked_conferences,
        'available_conferences': available_conferences,
        'total_bookings': booked_conferences,
        'approved_bookings': Booking.objects.filter(user=request.user, status='approved').count(),
        'pending_bookings': Booking.objects.filter(user=request.user, status='pending').count(),
        'rejected_bookings': Booking.objects.filter(user=request.user, status='rejected').count(),
    }
    
    # Manager-specific data
    if hasattr(request.user, 'is_manager') and request.user.is_manager():
        pending_approvals = Booking.objects.filter(
            user__department=request.user.department,
            status='pending'
        ).count()
        stats['pending_approvals'] = pending_approvals
    
    context = {
        'user_bookings': user_bookings,
        'upcoming_conferences': upcoming_conferences,
        'stats': stats,
    }
    return render(request, 'bookings/dashboard.html', context)

def conference_detail(request, pk):
    """Conference detail view"""
    conference = get_object_or_404(Conference, pk=pk)
    user_booking = None
    
    if request.user.is_authenticated:
        try:
            user_booking = Booking.objects.get(user=request.user, conference=conference)
        except Booking.DoesNotExist:
            pass
    
    context = {
        'conference': conference,
        'user_booking': user_booking,
        'available_seats': conference.available_seats() if hasattr(conference, 'available_seats') else conference.capacity
    }
    return render(request, 'bookings/conference_detail.html', context)

@login_required
def book_conference(request, pk):
    """Book a conference"""
    conference = get_object_or_404(Conference, pk=pk)
    
    # Check if conference is fully booked
    available_seats = getattr(conference, 'available_seats', lambda: conference.capacity)()
    if available_seats <= 0:
        messages.error(request, 'Sorry, this conference is fully booked.')
        return redirect('conference_detail', pk=pk)
    
    # Check if user already booked this conference
    existing_booking = Booking.objects.filter(user=request.user, conference=conference).first()
    if existing_booking:
        messages.error(request, 'You have already booked this conference.')
        return redirect('conference_detail', pk=pk)
    
    if request.method == 'POST':
        justification = request.POST.get('justification', '')
        
        try:
            booking = Booking.objects.create(
                user=request.user,
                conference=conference,
                justification=justification,
                status='pending' if getattr(conference, 'requires_approval', True) else 'approved'
            )
            
            status_message = 'pending approval' if booking.status == 'pending' else 'confirmed'
            messages.success(
                request, 
                f'Successfully submitted booking request for {conference.title}! Your booking is {status_message}.'
            )
            
            # Send notification email if needed
            if booking.status == 'pending' and hasattr(request.user, 'department') and request.user.department:
                # You can add email notification logic here
                pass
            
            return redirect('my_bookings')
            
        except IntegrityError:
            messages.error(request, 'You have already booked this conference.')
    
    return render(request, 'bookings/book_conference.html', {
        'conference': conference
    })

@login_required
def cancel_booking(request, pk):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    conference_title = booking.conference.title
    booking.delete()
    messages.success(request, f'Successfully cancelled booking for {conference_title}.')
    return redirect('my_bookings')



@login_required
def my_bookings(request):
    """User's booking list"""
    # Show all bookings to admin, only user's bookings otherwise
    is_admin_user = is_admin(request.user)
    if is_admin_user:
        bookings = Booking.objects.order_by('-booking_date').all()
    else:
        bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    return render(request, 'bookings/my_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'is_admin_user': is_admin_user,
    })

# Manager/Admin views
def is_manager_or_admin(user):
    """Check if user is manager or admin"""
    return (hasattr(user, 'is_manager') and user.is_manager()) or \
           (hasattr(user, 'is_admin') and user.is_admin()) or \
           user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_manager_or_admin)
def manage_bookings(request):
    """Manager view to manage team bookings"""
    # Get bookings based on user role
    if hasattr(request.user, 'is_admin') and request.user.is_admin():
        bookings = Booking.objects.all()
        print("Admin user - accessing all bookings", bookings)
    elif hasattr(request.user, 'department') and request.user.department:
        bookings = Booking.objects.filter(user__department=request.user.department)
    else:
        bookings = Booking.objects.none()
    print("Admin user - accessing all bookings", bookings)
    # Filter by status
    status_filter = request.GET.get('status', 'pending')
    if status_filter and status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
    
    bookings = bookings.order_by('-booking_date')
    
    # Pagination
    paginator = Paginator(bookings, 15)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    return render(request, 'bookings/manage_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
    })

@login_required
@user_passes_test(is_admin)
def approve_booking(request, pk):
    """Approve or reject a booking"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check permissions
    can_approve = False
    if (
        (hasattr(request.user, 'is_admin') and request.user.is_admin()) or
        request.user.is_staff or request.user.is_superuser
    ):
        can_approve = True
    elif (hasattr(request.user, 'is_manager') and request.user.is_manager() and 
          hasattr(request.user, 'department') and hasattr(booking.user, 'department') and
          booking.user.department == request.user.department):
        can_approve = True
    
    if not can_approve:
        messages.error(request, 'You do not have permission to approve this booking.')
        return redirect('manage_bookings')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve':
            booking.status = 'approved'
            booking.approved_by = request.user
            booking.approved_date = timezone.now()
            booking.notes = comments
            booking.save()
            
            messages.success(request, f'Booking approved for {booking.user.get_full_name()}.')
            
            # Send notification email
            try:
                send_mail(
                    subject=f'Conference Booking Approved: {booking.conference.title}',
                    message=f'Your booking for {booking.conference.title} has been approved.',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@company.com'),
                    recipient_list=[booking.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
            
        elif action == 'reject':
            booking.status = 'rejected'
            booking.rejection_reason = comments
            booking.save()
            
            messages.success(request, f'Booking rejected for {booking.user.get_full_name()}.')
            
            # Send notification email
            try:
                send_mail(
                    subject=f'Conference Booking Rejected: {booking.conference.title}',
                    message=f'Your booking for {booking.conference.title} has been rejected. Reason: {comments}',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@company.com'),
                    recipient_list=[booking.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
    
    return redirect('manage_bookings')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def reports(request):
    """Generate reports (admin only)"""
    # Basic statistics
    total_bookings = Booking.objects.count()
    approved_bookings = Booking.objects.filter(status='approved').count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    rejected_bookings = Booking.objects.filter(status='rejected').count()
    
    # Monthly booking trends (last 12 months)
    from django.db.models.functions import TruncMonth
    
    monthly_bookings = Booking.objects.filter(
        booking_date__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month=TruncMonth('booking_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Department statistics (if User model has department)
    dept_stats = []
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if hasattr(User, 'department'):
            from accounts.models import Department
            dept_stats = Department.objects.annotate(
                total_bookings=Count('user__booking'),
                approved_bookings=Count('user__booking', filter=Q(user__booking__status='approved')),
                total_cost=Sum('user__booking__conference__price', filter=Q(user__booking__status='approved'))
            ).filter(total_bookings__gt=0)
    except Exception as e:
        print(f"Department stats error: {e}")
    
    context = {
        'total_bookings': total_bookings,
        'approved_bookings': approved_bookings,
        'pending_bookings': pending_bookings,
        'rejected_bookings': rejected_bookings,
        'dept_stats': dept_stats,
        'monthly_bookings': monthly_bookings,
    }
    return render(request, 'bookings/reports.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def export_bookings(request):
    """Export bookings to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'User', 'Email', 'Department', 'Conference', 'Conference Date', 
        'Booking Status', 'Booking Date', 'Cost', 'Approved By'
    ])
    
    bookings = Booking.objects.select_related('user', 'conference', 'approved_by').all()
    
    for booking in bookings:
        writer.writerow([
            booking.user.get_full_name() if hasattr(booking.user, 'get_full_name') else booking.user.username,
            booking.user.email,
            getattr(booking.user, 'department', 'N/A'),
            booking.conference.title,
            # booking.conference.date,
            booking.get_status_display(),
            booking.booking_date.strftime('%Y-%m-%d %H:%M'),
            booking.conference.price,
            booking.approved_by.get_full_name() if booking.approved_by else '',
        ])
    
    return response

# Authentication views
def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the conference booking system.')
            return redirect('dashboard' if user.is_authenticated else 'home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

# API views (optional)
@login_required
def api_conference_availability(request, pk):
    """API endpoint to check conference availability"""
    try:
        conference = get_object_or_404(Conference, pk=pk)
        available_seats = getattr(conference, 'available_seats', lambda: conference.capacity)()
        
        return JsonResponse({
            'available_seats': available_seats,
            'total_capacity': conference.capacity,
            'is_available': available_seats > 0
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
def custom_logout(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

# Alternative POST-only logout view
@login_required
def secure_logout(request):
    """Secure logout view that only accepts POST requests"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    else:
        return redirect('home')
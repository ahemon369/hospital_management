from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('accounts:login')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def dashboard(request):
    from patients.models import Patient
    from doctors.models import Doctor
    from appointments.models import Appointment
    from billing.models import Bill
    from pharmacy.models import Medicine
    from django.db.models import Sum
    
    today = timezone.now().date()
    
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    total_revenue = Bill.objects.filter(status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0
    recent_patients = Patient.objects.all().order_by('-created_at')[:5]
    recent_appointments = Appointment.objects.all().order_by('-created_at')[:5]
    low_stock_medicines = Medicine.objects.filter(stock_quantity__lt=10)
    
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'total_revenue': total_revenue,
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
        'low_stock_medicines': low_stock_medicines,
    }
    
    return render(request, 'dashboard.html', context)

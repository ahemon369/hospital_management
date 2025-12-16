from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Appointment
from patients.models import Patient
from doctors.models import Doctor
import random
import string

def generate_appointment_id():
    """Generate unique appointment ID"""
    prefix = "APT"
    random_num = ''.join(random.choices(string.digits, k=6))
    appointment_id = f"{prefix}{random_num}"
    
    # Check if ID already exists
    while Appointment.objects.filter(appointment_id=appointment_id).exists():
        random_num = ''.join(random.choices(string.digits, k=6))
        appointment_id = f"{prefix}{random_num}"
    
    return appointment_id


@login_required
def appointment_list(request):
    """Display list of all appointments"""
    appointments = Appointment.objects.all().select_related('patient__user', 'doctor__user').order_by('-appointment_date', '-appointment_time')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Count by status
    pending = Appointment.objects.filter(status='PENDING').count()
    confirmed = Appointment.objects.filter(status='CONFIRMED').count()
    completed = Appointment.objects.filter(status='COMPLETED').count()
    cancelled = Appointment.objects.filter(status='CANCELLED').count()
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed,
        'cancelled': cancelled,
    }
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def appointment_detail(request, pk):
    """Display detailed view of an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})


@login_required
def appointment_create(request):
    """Create a new appointment"""
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = request.POST.get('patient')
            doctor_id = request.POST.get('doctor')
            appointment_date = request.POST.get('appointment_date')
            appointment_time = request.POST.get('appointment_time')
            appointment_type = request.POST.get('appointment_type')
            symptoms = request.POST.get('symptoms', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            # Validate required fields
            if not all([patient_id, doctor_id, appointment_date, appointment_time, appointment_type, symptoms]):
                messages.error(request, 'Please fill in all required fields!')
                patients = Patient.objects.all().select_related('user')
                doctors = Doctor.objects.filter(is_available=True).select_related('user')
                return render(request, 'appointments/appointment_form.html', {
                    'patients': patients,
                    'doctors': doctors,
                    'is_update': False
                })
            
            # Get patient and doctor objects
            patient = get_object_or_404(Patient, pk=patient_id)
            doctor = get_object_or_404(Doctor, pk=doctor_id)
            
            # Generate appointment ID
            appointment_id = generate_appointment_id()
            
            # Create appointment
            appointment = Appointment.objects.create(
                appointment_id=appointment_id,
                patient=patient,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                appointment_type=appointment_type,
                symptoms=symptoms,
                notes=notes,
                status='PENDING'
            )
            
            messages.success(request, f'Appointment booked successfully! Appointment ID: {appointment_id}')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating appointment: {str(e)}')
            patients = Patient.objects.all().select_related('user')
            doctors = Doctor.objects.filter(is_available=True).select_related('user')
            return render(request, 'appointments/appointment_form.html', {
                'patients': patients,
                'doctors': doctors,
                'is_update': False
            })
    
    # GET request - show form
    patients = Patient.objects.all().select_related('user')
    doctors = Doctor.objects.filter(is_available=True).select_related('user')
    
    # Get URL parameters for auto-selection
    selected_patient = request.GET.get('patient')
    selected_doctor = request.GET.get('doctor')
    
    context = {
        'patients': patients,
        'doctors': doctors,
        'selected_patient': selected_patient,
        'selected_doctor': selected_doctor,
        'is_update': False
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_update(request, pk):
    """Update an existing appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        try:
            # Update appointment fields
            appointment.appointment_date = request.POST.get('appointment_date')
            appointment.appointment_time = request.POST.get('appointment_time')
            appointment.appointment_type = request.POST.get('appointment_type')
            appointment.symptoms = request.POST.get('symptoms', '').strip()
            appointment.notes = request.POST.get('notes', '').strip()
            
            # Validate required fields
            if not all([appointment.appointment_date, appointment.appointment_time, 
                       appointment.appointment_type, appointment.symptoms]):
                messages.error(request, 'Please fill in all required fields!')
                patients = Patient.objects.all().select_related('user')
                doctors = Doctor.objects.all().select_related('user')
                return render(request, 'appointments/appointment_form.html', {
                    'appointment': appointment,
                    'patients': patients,
                    'doctors': doctors,
                    'is_update': True
                })
            
            appointment.save()
            
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating appointment: {str(e)}')
    
    # GET request - show form with appointment data
    patients = Patient.objects.all().select_related('user')
    doctors = Doctor.objects.all().select_related('user')
    
    context = {
        'appointment': appointment,
        'patients': patients,
        'doctors': doctors,
        'is_update': True
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_delete(request, pk):
    """Delete an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment_id = appointment.appointment_id
        patient_name = appointment.patient.user.get_full_name()
        appointment.delete()
        messages.success(request, f'Appointment {appointment_id} for {patient_name} deleted successfully!')
        return redirect('appointments:appointment_list')
    
    return redirect('appointments:appointment_detail', pk=pk)


@login_required
def appointment_confirm(request, pk):
    """Confirm a pending appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment.status = 'CONFIRMED'
        appointment.save()
        messages.success(request, f'Appointment {appointment.appointment_id} confirmed successfully!')
        return redirect('appointments:appointment_detail', pk=pk)
    
    return redirect('appointments:appointment_detail', pk=pk)


@login_required
def appointment_complete(request, pk):
    """Mark appointment as completed"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment.status = 'COMPLETED'
        appointment.save()
        messages.success(request, f'Appointment {appointment.appointment_id} marked as completed!')
        return redirect('appointments:appointment_detail', pk=pk)
    
    return redirect('appointments:appointment_detail', pk=pk)


@login_required
def appointment_cancel(request, pk):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.warning(request, f'Appointment {appointment.appointment_id} has been cancelled.')
        return redirect('appointments:appointment_detail', pk=pk)
    
    return redirect('appointments:appointment_detail', pk=pk)
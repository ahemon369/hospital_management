from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Patient

@login_required
def patient_list(request):
    patients = Patient.objects.all().select_related('user')
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            Q(patient_id__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    context = {
        'patients': patients,
        'search_query': search_query,
        'total_patients': Patient.objects.count(),
    }
    return render(request, 'patients/patient_list.html', context)


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    from appointments.models import Appointment
    from billing.models import Bill
    from medical_records.models import MedicalRecord
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    bills = Bill.objects.filter(patient=patient).order_by('-created_at')
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-visit_date')
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='COMPLETED').count()
    pending_appointments = appointments.filter(status='PENDING').count()
    total_records = medical_records.count()
    
    context = {
        'patient': patient,
        'appointments': appointments[:10],
        'bills': bills[:10],
        'medical_records': medical_records[:5],
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
        'total_records': total_records,
    }
    return render(request, 'patients/patient_detail.html', context)


@login_required
def patient_create(request):
    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                password=request.POST.get('password')
            )
            patient = Patient.objects.create(
                user=user,
                patient_id=request.POST.get('patient_id'),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender'),
                blood_group=request.POST.get('blood_group'),
                phone_number=request.POST.get('phone_number'),
                address=request.POST.get('address'),
                emergency_contact=request.POST.get('emergency_contact'),
                medical_history=request.POST.get('medical_history', ''),
                allergies=request.POST.get('allergies', ''),
            )
            messages.success(request, 'Patient registered successfully!')
            return redirect('patients:patient_detail', pk=patient.pk)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'patients/patient_form.html')


@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        try:
            patient.user.first_name = request.POST.get('first_name')
            patient.user.last_name = request.POST.get('last_name')
            patient.user.email = request.POST.get('email')
            patient.user.save()
            patient.date_of_birth = request.POST.get('date_of_birth')
            patient.gender = request.POST.get('gender')
            patient.blood_group = request.POST.get('blood_group')
            patient.phone_number = request.POST.get('phone_number')
            patient.address = request.POST.get('address')
            patient.emergency_contact = request.POST.get('emergency_contact')
            patient.save()
            messages.success(request, 'Patient updated successfully!')
            return redirect('patients:patient_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    context = {'patient': patient, 'is_update': True}
    return render(request, 'patients/patient_form.html', context)


@login_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.user.delete()
        messages.success(request, 'Patient deleted successfully!')
        return redirect('patients:patient_list')
    return redirect('patients:patient_detail', pk=pk)


@login_required
@require_POST
def patient_quick_create(request):
    """Quick patient creation via AJAX for billing"""
    try:
        with transaction.atomic():
            # Get form data
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            date_of_birth = request.POST.get('date_of_birth')
            gender = request.POST.get('gender')
            address = request.POST.get('address', '').strip()
            
            # Validate required fields
            if not all([first_name, last_name, email, date_of_birth, gender]):
                return JsonResponse({
                    'success': False,
                    'error': 'All required fields must be filled!'
                })
            
            # Check if email exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email already exists! Please use a different email.'
                })
            
            # Generate unique username
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='temp123456'  # Temporary password
            )
            
            # Create patient (patient_id will be auto-generated by model)
            patient = Patient.objects.create(
                user=user,
                date_of_birth=date_of_birth,
                gender=gender,
                phone_number=phone_number or '',
                address=address or ''
            )
            
            return JsonResponse({
                'success': True,
                'patient': {
                    'id': patient.pk,
                    'patient_id': patient.patient_id,
                    'name': patient.get_full_name(),
                    'email': email
                },
                'message': 'Patient created successfully!'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error creating patient: {str(e)}'
        })
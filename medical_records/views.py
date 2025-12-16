from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import MedicalRecord
from patients.models import Patient
from doctors.models import Doctor

@login_required
def medical_record_list(request):
    """Display list of all medical records"""
    records = MedicalRecord.objects.all().select_related('patient__user', 'doctor__user').order_by('-visit_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        records = records.filter(
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(patient__patient_id__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__last_name__icontains=search_query) |
            Q(diagnosis__icontains=search_query)
        )
    
    context = {
        'records': records,
        'search_query': search_query,
        'total_records': MedicalRecord.objects.count(),
    }
    return render(request, 'medical_records/medical_record_list.html', context)


@login_required
def medical_record_detail(request, pk):
    """Display detailed view of a medical record"""
    record = get_object_or_404(MedicalRecord, pk=pk)
    return render(request, 'medical_records/medical_record_detail.html', {'record': record})


@login_required
def medical_record_create(request):
    """Create a new medical record"""
    if request.method == 'POST':
        try:
            # Get patient and doctor
            patient_id = request.POST.get('patient')
            doctor_id = request.POST.get('doctor')
            
            if not patient_id or not doctor_id:
                messages.error(request, 'Please select both patient and doctor!')
                patients = Patient.objects.all().select_related('user')
                doctors = Doctor.objects.all().select_related('user')
                return render(request, 'medical_records/medical_record_form.html', {
                    'patients': patients,
                    'doctors': doctors,
                    'is_update': False
                })
            
            patient = get_object_or_404(Patient, pk=patient_id)
            doctor = get_object_or_404(Doctor, pk=doctor_id)
            
            # Get visit information
            visit_date = request.POST.get('visit_date')
            visit_type = request.POST.get('visit_type')
            
            # Get vital signs
            temperature = request.POST.get('temperature', '').strip()
            blood_pressure = request.POST.get('blood_pressure', '').strip()
            heart_rate = request.POST.get('heart_rate', '').strip()
            weight = request.POST.get('weight', '').strip()
            
            # Get medical information
            chief_complaint = request.POST.get('chief_complaint', '').strip()
            symptoms = request.POST.get('symptoms', '').strip()
            diagnosis = request.POST.get('diagnosis', '').strip()
            prescription = request.POST.get('prescription', '').strip()
            lab_tests = request.POST.get('lab_tests', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            # Validate required fields
            if not all([visit_date, visit_type, chief_complaint, diagnosis]):
                messages.error(request, 'Visit date, visit type, chief complaint, and diagnosis are required!')
                patients = Patient.objects.all().select_related('user')
                doctors = Doctor.objects.all().select_related('user')
                return render(request, 'medical_records/medical_record_form.html', {
                    'patients': patients,
                    'doctors': doctors,
                    'is_update': False
                })
            
            # Create medical record
            record = MedicalRecord.objects.create(
                patient=patient,
                doctor=doctor,
                visit_date=visit_date,
                visit_type=visit_type,
                temperature=float(temperature) if temperature else None,
                blood_pressure=blood_pressure,
                heart_rate=int(heart_rate) if heart_rate else None,
                weight=float(weight) if weight else None,
                chief_complaint=chief_complaint,
                symptoms=symptoms,
                diagnosis=diagnosis,
                prescription=prescription,
                lab_tests=lab_tests,
                notes=notes
            )
            
            messages.success(request, f'Medical record created successfully for {patient.get_full_name()}!')
            return redirect('medical_records:medical_record_detail', pk=record.pk)
            
        except ValueError as e:
            messages.error(request, 'Invalid number format in vital signs. Please check temperature, heart rate, and weight.')
            patients = Patient.objects.all().select_related('user')
            doctors = Doctor.objects.all().select_related('user')
            return render(request, 'medical_records/medical_record_form.html', {
                'patients': patients,
                'doctors': doctors,
                'is_update': False
            })
        except Exception as e:
            messages.error(request, f'Error creating medical record: {str(e)}')
            patients = Patient.objects.all().select_related('user')
            doctors = Doctor.objects.all().select_related('user')
            return render(request, 'medical_records/medical_record_form.html', {
                'patients': patients,
                'doctors': doctors,
                'is_update': False
            })
    
    # GET request - show form
    patients = Patient.objects.all().select_related('user')
    doctors = Doctor.objects.all().select_related('user')
    
    context = {
        'patients': patients,
        'doctors': doctors,
        'is_update': False
    }
    return render(request, 'medical_records/medical_record_form.html', context)


@login_required
def medical_record_update(request, pk):
    """Update an existing medical record"""
    record = get_object_or_404(MedicalRecord, pk=pk)
    
    if request.method == 'POST':
        try:
            # Get doctor (patient cannot be changed)
            doctor_id = request.POST.get('doctor')
            if doctor_id:
                record.doctor = get_object_or_404(Doctor, pk=doctor_id)
            
            # Update visit information
            record.visit_date = request.POST.get('visit_date')
            record.visit_type = request.POST.get('visit_type')
            
            # Update vital signs
            temperature = request.POST.get('temperature', '').strip()
            blood_pressure = request.POST.get('blood_pressure', '').strip()
            heart_rate = request.POST.get('heart_rate', '').strip()
            weight = request.POST.get('weight', '').strip()
            
            record.temperature = float(temperature) if temperature else None
            record.blood_pressure = blood_pressure
            record.heart_rate = int(heart_rate) if heart_rate else None
            record.weight = float(weight) if weight else None
            
            # Update medical information
            record.chief_complaint = request.POST.get('chief_complaint', '').strip()
            record.symptoms = request.POST.get('symptoms', '').strip()
            record.diagnosis = request.POST.get('diagnosis', '').strip()
            record.prescription = request.POST.get('prescription', '').strip()
            record.lab_tests = request.POST.get('lab_tests', '').strip()
            record.notes = request.POST.get('notes', '').strip()
            
            # Validate required fields
            if not all([record.visit_date, record.visit_type, record.chief_complaint, record.diagnosis]):
                messages.error(request, 'Visit date, visit type, chief complaint, and diagnosis are required!')
                patients = Patient.objects.all().select_related('user')
                doctors = Doctor.objects.all().select_related('user')
                return render(request, 'medical_records/medical_record_form.html', {
                    'record': record,
                    'patients': patients,
                    'doctors': doctors,
                    'is_update': True
                })
            
            record.save()
            
            messages.success(request, 'Medical record updated successfully!')
            return redirect('medical_records:medical_record_detail', pk=record.pk)
            
        except ValueError:
            messages.error(request, 'Invalid number format in vital signs. Please check temperature, heart rate, and weight.')
        except Exception as e:
            messages.error(request, f'Error updating medical record: {str(e)}')
    
    # GET request - show form with record data
    patients = Patient.objects.all().select_related('user')
    doctors = Doctor.objects.all().select_related('user')
    
    context = {
        'record': record,
        'patients': patients,
        'doctors': doctors,
        'is_update': True
    }
    return render(request, 'medical_records/medical_record_form.html', context)


@login_required
def medical_record_delete(request, pk):
    """Delete a medical record"""
    record = get_object_or_404(MedicalRecord, pk=pk)
    
    if request.method == 'POST':
        patient_name = record.patient.get_full_name()
        record.delete()
        messages.success(request, f'Medical record for {patient_name} deleted successfully!')
        return redirect('medical_records:medical_record_list')
    
    return redirect('medical_records:medical_record_detail', pk=pk)


@login_required
def medical_record_print(request, pk):
    """Generate printable medical record"""
    record = get_object_or_404(MedicalRecord, pk=pk)
    return render(request, 'medical_records/medical_record_print.html', {'record': record})
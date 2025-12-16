from django.contrib.auth.models import User
from accounts.models import UserProfile
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from pharmacy.models import Medicine
from billing.models import Bill
from medical_records.models import MedicalRecord
from django.utils import timezone
from datetime import timedelta
import random

def create_sample_data():
    print("Creating sample data...")
    
    # Create admin user
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@hospital.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        UserProfile.objects.create(
            user=admin,
            role='ADMIN',
            phone_number='01700000000'
        )
        print("✓ Admin user created (username: admin, password: admin123)")
    
    # Create doctors
    doctors_data = [
        {
            'username': 'dr_smith',
            'email': 'smith@hospital.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'employee_id': 'DOC-001',
            'specialization': 'Cardiology',
            'qualification': 'MBBS, MD',
            'experience': 10,
            'phone': '01711111111',
            'fee': 500
        },
        {
            'username': 'dr_jones',
            'email': 'jones@hospital.com',
            'first_name': 'Sarah',
            'last_name': 'Jones',
            'employee_id': 'DOC-002',
            'specialization': 'Pediatrics',
            'qualification': 'MBBS, DCH',
            'experience': 8,
            'phone': '01722222222',
            'fee': 400
        },
    ]
    
    for doc_data in doctors_data:
        if not User.objects.filter(username=doc_data['username']).exists():
            user = User.objects.create_user(
                username=doc_data['username'],
                email=doc_data['email'],
                password='doctor123',
                first_name=doc_data['first_name'],
                last_name=doc_data['last_name']
            )
            
            Doctor.objects.create(
                user=user,
                employee_id=doc_data['employee_id'],
                specialization=doc_data['specialization'],
                qualification=doc_data['qualification'],
                experience=doc_data['experience'],
                phone_number=doc_data['phone'],
                consultation_fee=doc_data['fee'],
                available_days='Mon-Sat',
                available_time='9:00 AM - 5:00 PM',
            )
            
            UserProfile.objects.create(
                user=user,
                role='DOCTOR',
                phone_number=doc_data['phone']
            )
            print(f"✓ Doctor created: {doc_data['first_name']} {doc_data['last_name']}")
    
    # Create patients
    patients_data = [
        {
            'username': 'patient1',
            'email': 'patient1@email.com',
            'first_name': 'MD AMRAN HOSSIN',
            'last_name': 'EMON',
            'patient_id': 'PAT-00001',
            'dob': '2005-01-15',
            'gender': 'M',
            'blood_group': 'A+',
            'phone': '01610974369'
        },
        {
            'username': 'patient2',
            'email': 'patient2@email.com',
            'first_name': 'Rawnak',
            'last_name': 'Kaif',
            'patient_id': 'PAT-00002',
            'dob': '2025-01-01',
            'gender': 'M',
            'blood_group': 'B+',
            'phone': '01810974369'
        },
        {
            'username': 'patient3',
            'email': 'patient3@email.com',
            'first_name': 'Imam',
            'last_name': 'HASAN',
            'patient_id': 'PAT-00003',
            'dob': '2025-01-01',
            'gender': 'F',
            'blood_group': 'A-',
            'phone': '01610974369'
        },
    ]
    
    for pat_data in patients_data:
        if not User.objects.filter(username=pat_data['username']).exists():
            user = User.objects.create_user(
                username=pat_data['username'],
                email=pat_data['email'],
                password='patient123',
                first_name=pat_data['first_name'],
                last_name=pat_data['last_name']
            )
            
            Patient.objects.create(
                user=user,
                patient_id=pat_data['patient_id'],
                date_of_birth=pat_data['dob'],
                gender=pat_data['gender'],
                blood_group=pat_data['blood_group'],
                phone_number=pat_data['phone'],
                address='Dhaka, Bangladesh',
                emergency_contact=pat_data['phone']
            )
            print(f"✓ Patient created: {pat_data['first_name']} {pat_data['last_name']}")
    
    # Create medicines
    medicines_data = [
        {
            'medicine_id': 'MED-00001',
            'name': 'Napa',
            'category': 'Napa',
            'manufacturer': 'SquRE',
            'stock': 1100100,
            'purchase_price': 1.50,
            'selling_price': 2.00,
            'expiry': '1916-04-17'
        },
    ]
    
    for med_data in medicines_data:
        if not Medicine.objects.filter(medicine_id=med_data['medicine_id']).exists():
            Medicine.objects.create(
                medicine_id=med_data['medicine_id'],
                name=med_data['name'],
                category=med_data['category'],
                manufacturer=med_data['manufacturer'],
                stock_quantity=med_data['stock'],
                purchase_price=med_data['purchase_price'],
                selling_price=med_data['selling_price'],
                expiry_date=med_data['expiry']
            )
            print(f"✓ Medicine created: {med_data['name']}")
    
    # Create appointments
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    
    if patients and doctors:
        appointments_data = [
            {
                'appointment_id': 'APT-00001',
                'patient': patients[0],
                'doctor': doctors[0],
                'date': timezone.now().date(),
                'time': '18:00',
                'type': 'Dental',
                'symptoms': 'edqscx',
                'status': 'COMPLETED'
            },
            {
                'appointment_id': 'APT-00002',
                'patient': patients[1],
                'doctor': doctors[0],
                'date': timezone.now().date(),
                'time': '17:48',
                'type': 'Dental',
                'symptoms': 'Jor',
                'status': 'COMPLETED'
            },
        ]
        
        for apt_data in appointments_data:
            if not Appointment.objects.filter(appointment_id=apt_data['appointment_id']).exists():
                Appointment.objects.create(
                    appointment_id=apt_data['appointment_id'],
                    patient=apt_data['patient'],
                    doctor=apt_data['doctor'],
                    appointment_date=apt_data['date'],
                    appointment_time=apt_data['time'],
                    appointment_type=apt_data['type'],
                    symptoms=apt_data['symptoms'],
                    status=apt_data['status']
                )
                print(f"✓ Appointment created: {apt_data['appointment_id']}")
    
    # Create medical records
    if patients and doctors:
        records_data = [
            {
                'record_id': 'MED-00001',
                'patient': patients[0],
                'doctor': doctors[0],
                'visit_date': '2025-12-10',
                'visit_time': '08:52',
                'symptoms': 'Premikar Obav',
                'diagnosis': 'HeatBit',
                'prescription': '1 cahmos kola',
                'tests': 'Hat kata',
                'follow_up': '2025-12-17'
            },
        ]
        
        for rec_data in records_data:
            if not MedicalRecord.objects.filter(record_id=rec_data['record_id']).exists():
                MedicalRecord.objects.create(
                    record_id=rec_data['record_id'],
                    patient=rec_data['patient'],
                    doctor=rec_data['doctor'],
                    visit_date=rec_data['visit_date'],
                    visit_time=rec_data['visit_time'],
                    symptoms=rec_data['symptoms'],
                    diagnosis=rec_data['diagnosis'],
                    prescription=rec_data['prescription'],
                    tests_recommended=rec_data['tests'],
                    follow_up_date=rec_data['follow_up']
                )
                print(f"✓ Medical record created: {rec_data['record_id']}")
    
    # Create bills
    if patients:
        bills_data = [
            {
                'bill_number': 'BILL-00001',
                'patient': patients[0],
                'consultation': 16.00,
                'medicine': 0,
                'lab': 0,
                'paid': 940.00,
                'payment_method': 'CASH',
                'status': 'PAID'
            },
            {
                'bill_number': 'BILL-00002',
                'patient': patients[1],
                'consultation': 1000.00,
                'medicine': 0,
                'lab': 0,
                'paid': 1000.00,
                'payment_method': 'CASH',
                'status': 'PAID'
            },
            {
                'bill_number': 'BILL-00003',
                'patient': patients[2],
                'consultation': 2000.00,
                'medicine': 0,
                'lab': 0,
                'paid': 0.00,
                'payment_method': '',
                'status': 'UNPAID'
            },
        ]
        
        for bill_data in bills_data:
            if not Bill.objects.filter(bill_number=bill_data['bill_number']).exists():
                Bill.objects.create(
                    bill_number=bill_data['bill_number'],
                    patient=bill_data['patient'],
                    consultation_fee=bill_data['consultation'],
                    medicine_charges=bill_data['medicine'],
                    lab_charges=bill_data['lab'],
                    amount_paid=bill_data['paid'],
                    payment_method=bill_data['payment_method'],
                    payment_date=timezone.now().date() if bill_data['paid'] > 0 else None
                )
                print(f"✓ Bill created: {bill_data['bill_number']}")
    
    print("\n✅ Sample data creation completed!")
    print("\nLogin credentials:")
    print("Admin - username: admin, password: admin123")
    print("Doctor - username: dr_smith, password: doctor123")
    print("Patient - username: patient1, password: patient123")

if __name__ == '__main__':
    create_sample_data()
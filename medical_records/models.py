from django.db import models
from patients.models import Patient
from doctors.models import Doctor

class MedicalRecord(models.Model):
    VISIT_TYPE_CHOICES = [
        ('CONSULTATION', 'Consultation'),
        ('FOLLOWUP', 'Follow-up'),
        ('EMERGENCY', 'Emergency'),
        ('ROUTINE', 'Routine Checkup'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_records')
    visit_date = models.DateField()
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES)
    
    # Vital Signs
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Medical Information
    chief_complaint = models.TextField()
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True)
    lab_tests = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.visit_date}"
    
    class Meta:
        ordering = ['-visit_date']
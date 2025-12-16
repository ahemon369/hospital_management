from django.db import models
from patients.models import Patient
from doctors.models import Doctor

class Appointment(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')]
    
    appointment_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_type = models.CharField(max_length=100)
    symptoms = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient}"
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-appointment_date', '-appointment_time']
from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone_number = models.CharField(max_length=15, blank=True)
    room_number = models.CharField(max_length=20, blank=True)
    available_days = models.CharField(max_length=100, blank=True)
    available_time = models.CharField(max_length=100, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-generate employee_id if not exists
        if not self.employee_id:
            last_doctor = Doctor.objects.filter(
                employee_id__isnull=False
            ).exclude(
                employee_id=''
            ).order_by('-id').first()
            
            if last_doctor and last_doctor.employee_id:
                try:
                    # Extract number from format DOC-001
                    last_number = int(last_doctor.employee_id.split('-')[1])
                    self.employee_id = f'DOC-{last_number + 1:03d}'
                except (IndexError, ValueError):
                    # Fallback: count total doctors
                    total_doctors = Doctor.objects.count()
                    self.employee_id = f'DOC-{total_doctors + 1:03d}'
            else:
                self.employee_id = 'DOC-001'
        
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def __str__(self):
        return f"Dr. {self.get_full_name()} ({self.employee_id})"
    
    class Meta:
        ordering = ['-created_at']
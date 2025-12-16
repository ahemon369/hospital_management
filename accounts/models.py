from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [('ADMIN', 'Administrator'), ('DOCTOR', 'Doctor'), ('NURSE', 'Nurse'), ('RECEPTIONIST', 'Receptionist'), ('PHARMACIST', 'Pharmacist')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"
    
    class Meta:
        db_table = 'user_profiles'

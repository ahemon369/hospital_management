from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Employee(models.Model):
    DEPARTMENT_CHOICES = [
        ('ADMIN', 'Administration'),
        ('NURSING', 'Nursing'),
        ('PHARMACY', 'Pharmacy'),
        ('LAB', 'Laboratory'),
        ('RECEPTION', 'Reception'),
        ('ACCOUNTS', 'Accounts'),
        ('IT', 'IT Support'),
        ('CLEANING', 'Cleaning'),
        ('SECURITY', 'Security'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    DESIGNATION_CHOICES = [
        ('MANAGER', 'Manager'),
        ('SUPERVISOR', 'Supervisor'),
        ('STAFF', 'Staff'),
        ('ASSISTANT', 'Assistant'),
        ('HEAD', 'Head'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ON_LEAVE', 'On Leave'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='employees/', blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    phone = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15)
    address = models.TextField()
    
    # Employment Details
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES)
    join_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Documents
    nid_number = models.CharField(max_length=20, blank=True)
    bank_account = models.CharField(max_length=30, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    @property
    def age(self):
        from django.utils import timezone
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'


class Salary(models.Model):
    PAYMENT_STATUS = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partial'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    month = models.DateField()  # First day of the month
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='UNPAID')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.month.strftime('%B %Y')}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total
        self.total_amount = self.basic_salary + self.bonus - self.deductions
        # Update status
        if self.amount_paid >= self.total_amount:
            self.payment_status = 'PAID'
        elif self.amount_paid > 0:
            self.payment_status = 'PARTIAL'
        else:
            self.payment_status = 'UNPAID'
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-month']
        unique_together = ['employee', 'month']
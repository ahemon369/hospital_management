from django.db import models
from django.core.validators import MinValueValidator

class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('BANK', 'Bank Account'),
        ('CASH', 'Cash'),
        ('MOBILE_BANKING', 'Mobile Banking'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('CLOSED', 'Closed'),
    ]
    
    account_number = models.CharField(max_length=50, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    bank_name = models.CharField(max_length=100, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account_name} - {self.account_number}"
    
    class Meta:
        ordering = ['-created_at']


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('TRANSFER', 'Transfer'),
    ]
    
    CATEGORY_CHOICES = [
        # Income Categories
        ('CONSULTATION', 'Consultation Fee'),
        ('MEDICINE_SALE', 'Medicine Sale'),
        ('LAB_TEST', 'Lab Test'),
        ('ADMISSION', 'Admission Fee'),
        ('OTHER_INCOME', 'Other Income'),
        
        # Expense Categories
        ('SALARY', 'Salary Payment'),
        ('PURCHASE', 'Purchase'),
        ('UTILITY', 'Utility Bills'),
        ('RENT', 'Rent'),
        ('MAINTENANCE', 'Maintenance'),
        ('MEDICINE_PURCHASE', 'Medicine Purchase'),
        ('EQUIPMENT', 'Equipment'),
        ('OTHER_EXPENSE', 'Other Expense'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('BKASH', 'bKash'),
        ('NAGAD', 'Nagad'),
        ('CARD', 'Card'),
        ('CHEQUE', 'Cheque'),
    ]
    
    transaction_id = models.CharField(max_length=50, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type} - ৳{self.amount}"
    
    def save(self, *args, **kwargs):
        # Update account balance
        if not self.pk:  # New transaction
            if self.transaction_type == 'INCOME':
                self.account.balance += self.amount
            elif self.transaction_type == 'EXPENSE':
                self.account.balance -= self.amount
            self.account.save()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-date', '-created_at']


class Budget(models.Model):
    category = models.CharField(max_length=30, choices=Transaction.CATEGORY_CHOICES)
    month = models.DateField()  # First day of the month
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.month.strftime('%B %Y')}"
    
    @property
    def remaining_amount(self):
        return self.allocated_amount - self.spent_amount
    
    @property
    def utilization_percentage(self):
        if self.allocated_amount > 0:
            return (self.spent_amount / self.allocated_amount) * 100
        return 0
    
    class Meta:
        ordering = ['-month']
        unique_together = ['category', 'month']


class Expense(models.Model):
    expense_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, choices=Transaction.CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    paid_to = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=20, choices=Transaction.PAYMENT_METHOD_CHOICES)
    date = models.DateField()
    description = models.TextField()
    receipt_number = models.CharField(max_length=50, blank=True)
    approved_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.expense_id} - ৳{self.amount}"
    
    class Meta:
        ordering = ['-date']
from django.db import models
from django.core.exceptions import ValidationError

class Bill(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partial Payment'),
    ]
    
    bill_number = models.CharField(max_length=20, unique=True, blank=True)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='bills')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def subtotal(self):
        """Calculate subtotal before discount and tax"""
        return self.consultation_fee + self.medicine_charges + self.lab_charges + self.other_charges
    
    def save(self, *args, **kwargs):
        # Generate bill number only if it's empty
        if not self.bill_number:
            # Get last bill with a valid bill_number
            last_bill = Bill.objects.filter(
                bill_number__isnull=False
            ).exclude(
                bill_number=''
            ).order_by('-id').first()
            
            if last_bill and last_bill.bill_number:
                try:
                    # Extract number from format BILL-00001
                    last_number = int(last_bill.bill_number.split('-')[1])
                    self.bill_number = f'BILL-{last_number + 1:05d}'
                except (IndexError, ValueError):
                    # Fallback: count total bills
                    total_bills = Bill.objects.count()
                    self.bill_number = f'BILL-{total_bills + 1:05d}'
            else:
                self.bill_number = 'BILL-00001'
        
        # Calculate balance
        self.balance = self.total_amount - self.amount_paid
        
        # Update status based on payment
        if self.amount_paid <= 0:
            self.status = 'UNPAID'
        elif self.amount_paid >= self.total_amount:
            self.status = 'PAID'
            self.balance = 0
        else:
            self.status = 'PARTIAL'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.bill_number} - {self.patient.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'
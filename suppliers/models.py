from django.db import models
from django.core.validators import MinValueValidator

class Supplier(models.Model):
    CATEGORY_CHOICES = [
        ('MEDICINE', 'Medicine'),
        ('EQUIPMENT', 'Equipment'),
        ('FOOD', 'Food & Catering'),
        ('STATIONERY', 'Stationery'),
        ('CLEANING', 'Cleaning Supplies'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BLACKLISTED', 'Blacklisted'),
    ]
    
    # Basic Information
    supplier_id = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Contact Details
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    # Business Details
    tin_number = models.CharField(max_length=20, blank=True)
    bank_account = models.CharField(max_length=30, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, 
                                 validators=[MinValueValidator(0)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.supplier_id} - {self.company_name}"
    
    class Meta:
        ordering = ['-created_at']


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateField()
    expected_delivery = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.order_number} - {self.supplier.company_name}"
    
    class Meta:
        ordering = ['-order_date']


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=200)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.item_name} - {self.quantity} units"
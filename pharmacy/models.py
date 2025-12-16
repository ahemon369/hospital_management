from django.db import models

class Medicine(models.Model):
    UNIT_CHOICES = [
        ('Piece', 'Piece'),
        ('Box', 'Box'),
        ('Bottle', 'Bottle'),
        ('Strip', 'Strip'),
        ('Vial', 'Vial'),
        ('Tube', 'Tube'),
    ]
    
    medicine_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stock_quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES)
    expiry_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.medicine_id})"
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level
    
    @property
    def profit_margin(self):
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.purchase_price) * 100
        return 0
    
    class Meta:
        ordering = ['-created_at']
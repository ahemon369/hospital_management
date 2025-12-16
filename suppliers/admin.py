# suppliers/admin.py
from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_id', 'company_name', 'category', 'status', 'rating']
    list_filter = ['category', 'status']
    search_fields = ['supplier_id', 'company_name']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'order_date', 'total_amount', 'status']
    list_filter = ['status', 'order_date']

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'item_name', 'quantity', 'unit_price', 'total_price']


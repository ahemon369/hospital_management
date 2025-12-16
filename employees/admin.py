# employees/admin.py
from django.contrib import admin
from .models import Employee, Salary

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'department', 'designation', 'status', 'salary']
    list_filter = ['department', 'designation', 'status']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'total_amount', 'amount_paid', 'payment_status']
    list_filter = ['payment_status', 'month']



# attendance/admin.py
from django.contrib import admin
from .models import Attendance, Leave, Shift, EmployeeShift

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__employee_id', 'employee__user__first_name']

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status']
    list_filter = ['leave_type', 'status']

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active']

@admin.register(EmployeeShift)
class EmployeeShiftAdmin(admin.ModelAdmin):
    list_display = ['employee', 'shift', 'effective_date', 'is_current']
    list_filter = ['is_current']

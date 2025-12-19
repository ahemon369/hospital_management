# attendance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from .models import Attendance, Leave, Shift, EmployeeShift

@login_required
def attendance_dashboard(request):
    today = timezone.now().date()
    current_time = timezone.now()
    
    # Get today's attendance
    attendances = Attendance.objects.filter(date=today).select_related('employee__user')
    
    # Calculate statistics
    total_present = attendances.filter(status='PRESENT').count()
    total_absent = attendances.filter(status='ABSENT').count()
    
    # Calculate on-duty (present but not checked out yet)
    on_duty_count = attendances.filter(
        status='PRESENT',
        check_out__isnull=True
    ).count()
    
    # Get pending leaves
    pending_leaves = Leave.objects.filter(status='PENDING').count()
    
    # Get recent attendance records for table
    recent_attendances = attendances[:10]
    
    # Get pending leave requests for sidebar
    pending_leave_requests = Leave.objects.filter(
        status='PENDING'
    ).select_related('employee__user')[:5]
    
    # Calculate weekly summary
    from datetime import timedelta
    week_start = today - timedelta(days=7)
    week_attendances = Attendance.objects.filter(
        date__gte=week_start,
        date__lte=today
    )
    
    total_week_records = week_attendances.count()
    week_present = week_attendances.filter(status='PRESENT').count()
    week_avg = int((week_present / total_week_records * 100)) if total_week_records > 0 else 0
    
    context = {
        'attendances': recent_attendances,
        'today': today,
        'current_time': current_time,
        'total_present': total_present,
        'total_absent': total_absent,
        'on_duty_count': on_duty_count,
        'pending_leaves': pending_leaves,
        'pending_leave_requests': pending_leave_requests,
        'week_avg': week_avg,
    }
    return render(request, 'attendance/attendance_dashboard.html', context)


@login_required
def mark_attendance(request):
    from employees.models import Employee
    
    today = timezone.now().date()
    employees = Employee.objects.all().select_related('user')
    
    if request.method == 'POST':
        # Handle attendance submission
        # This is a simplified version - you can expand this
        pass
    
    context = {
        'today': today,
        'employees': employees,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def attendance_report(request):
    from datetime import timedelta
    from django.db.models import Count, Q
    from employees.models import Employee
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Get filter parameters
    from_date = request.GET.get('from_date', month_start.strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', today.strftime('%Y-%m-%d'))
    
    # Get attendance records
    attendances = Attendance.objects.filter(
        date__gte=from_date,
        date__lte=to_date
    ).select_related('employee__user')
    
    # Calculate statistics
    total_records = attendances.count()
    total_present = attendances.filter(status='PRESENT').count()
    total_absent = attendances.filter(status='ABSENT').count()
    avg_attendance = int((total_present / total_records * 100)) if total_records > 0 else 0
    
    # Get unique departments from employees (using DEPARTMENT_CHOICES)
    from employees.models import Employee
    departments = Employee.objects.values_list('department', flat=True).distinct()
    
    department_stats = []
    total_late_count = 0
    total_on_leave_count = 0
    
    for dept_code in departments:
        # Get department name from choices
        dept_name = dict(Employee.DEPARTMENT_CHOICES).get(dept_code, dept_code)
        
        # Get employees in this department
        dept_employees = Employee.objects.filter(department=dept_code)
        dept_employee_count = dept_employees.count()
        
        if dept_employee_count == 0:
            continue
        
        # Get attendance for this department
        dept_attendances = attendances.filter(employee__department=dept_code)
        dept_present = dept_attendances.filter(status='PRESENT').count()
        dept_absent = dept_attendances.filter(status='ABSENT').count()
        dept_total = dept_attendances.count()
        
        # Calculate percentage
        dept_percent = int((dept_present / dept_total * 100)) if dept_total > 0 else 0
        
        # Count leaves
        dept_on_leave = Leave.objects.filter(
            employee__department=dept_code,
            status='APPROVED',
            start_date__lte=to_date,
            end_date__gte=from_date
        ).count()
        
        total_on_leave_count += dept_on_leave
        
        # Calculate average present/absent per day
        from datetime import datetime
        date_from = datetime.strptime(from_date, '%Y-%m-%d').date()
        date_to = datetime.strptime(to_date, '%Y-%m-%d').date()
        days_count = (date_to - date_from).days + 1
        
        avg_present = int(dept_present / days_count) if days_count > 0 else dept_present
        avg_absent = int(dept_absent / days_count) if days_count > 0 else dept_absent
        
        department_stats.append({
            'name': dept_name,
            'total_staff': dept_employee_count,
            'avg_present': avg_present,
            'avg_absent': avg_absent,
            'attendance_percent': dept_percent,
            'late_count': 0,  # Can be calculated based on check-in time
            'on_leave': dept_on_leave
        })
    
    # Calculate individual employee stats
    employees = Employee.objects.filter(status='ACTIVE')
    employee_stats = []
    
    for employee in employees:
        emp_attendances = attendances.filter(employee=employee)
        present_days = emp_attendances.filter(status='PRESENT').count()
        absent_days = emp_attendances.filter(status='ABSENT').count()
        total_days = emp_attendances.count()
        
        if total_days > 0:
            attendance_percent = int((present_days / total_days * 100))
            
            leave_count = Leave.objects.filter(
                employee=employee,
                status='APPROVED',
                start_date__lte=to_date,
                end_date__gte=from_date
            ).count()
            
            employee_stats.append({
                'employee': employee,
                'working_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': 0,  # Can be calculated
                'leave_days': leave_count,
                'attendance_percent': attendance_percent
            })
    
    # Calculate totals for footer
    total_staff = Employee.objects.filter(status='ACTIVE').count()
    total_present_sum = sum(dept['avg_present'] for dept in department_stats)
    total_absent_sum = sum(dept['avg_absent'] for dept in department_stats)
    
    context = {
        'attendances': attendances,
        'from_date': from_date,
        'to_date': to_date,
        'total_records': total_records,
        'total_present': total_present,
        'total_absent': total_absent,
        'avg_attendance': avg_attendance,
        'late_count': total_late_count,
        'department_stats': department_stats,
        'employee_stats': employee_stats,
        'total_staff': total_staff,
        'total_present_avg': total_present_sum,
        'total_absent_avg': total_absent_sum,
        'total_late': total_late_count,
        'total_on_leave': total_on_leave_count,
    }
    return render(request, 'attendance/attendance_report.html', context)


@login_required
def on_duty_list(request):
    today = timezone.now().date()
    current_hour = timezone.now().hour
    
    # Get employees currently on duty (checked in but not checked out)
    on_duty = Attendance.objects.filter(
        date=today,
        status='PRESENT',
        check_out__isnull=True
    ).select_related('employee__user')
    
    # Get shift counts separately
    day_shift_count = 0
    night_shift_count = 0
    emergency_shift_count = 0
    
    try:
        day_shift = Shift.objects.filter(name__icontains='Day').first()
        if day_shift:
            day_shift_count = EmployeeShift.objects.filter(
                shift=day_shift,
                is_current=True,
                employee__attendances__date=today,
                employee__attendances__status='PRESENT'
            ).count()
        
        night_shift = Shift.objects.filter(name__icontains='Night').first()
        if night_shift:
            night_shift_count = EmployeeShift.objects.filter(
                shift=night_shift,
                is_current=True,
                employee__attendances__date=today,
                employee__attendances__status='PRESENT'
            ).count()
        
        emergency_shift = Shift.objects.filter(name__icontains='Emergency').first()
        if emergency_shift:
            emergency_shift_count = EmployeeShift.objects.filter(
                shift=emergency_shift,
                is_current=True,
                employee__attendances__date=today,
                employee__attendances__status='PRESENT'
            ).count()
    except Exception as e:
        pass
    
    context = {
        'on_duty': on_duty,
        'today': today,
        'day_shift_count': day_shift_count,
        'night_shift_count': night_shift_count,
        'emergency_shift_count': emergency_shift_count,
        'total_on_duty': on_duty.count(),
    }
    return render(request, 'attendance/on_duty_list.html', context)


@login_required
def leave_list(request):
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    leave_type_filter = request.GET.get('leave_type', '')
    
    # Start with all leaves
    leaves = Leave.objects.all().select_related('employee__user')
    
    # Apply filters
    if status_filter:
        leaves = leaves.filter(status=status_filter.upper())
    if leave_type_filter:
        leaves = leaves.filter(leave_type=leave_type_filter.upper())
    
    # Order by start date (most recent first)
    leaves = leaves.order_by('-start_date')
    
    # Calculate statistics
    pending_count = Leave.objects.filter(status='PENDING').count()
    approved_count = Leave.objects.filter(status='APPROVED').count()
    rejected_count = Leave.objects.filter(status='REJECTED').count()
    
    # Get current leaves (people on leave today)
    today = timezone.now().date()
    on_leave_today = Leave.objects.filter(
        status='APPROVED',
        start_date__lte=today,
        end_date__gte=today
    ).count()
    
    context = {
        'leaves': leaves,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'on_leave_today': on_leave_today,
        'status_filter': status_filter,
        'leave_type_filter': leave_type_filter,
    }
    return render(request, 'attendance/leave_list.html', context)


@login_required
def leave_create(request):
    from employees.models import Employee
    
    if request.method == 'POST':
        # Handle leave creation
        employee_id = request.POST.get('employee')
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        try:
            employee = Employee.objects.get(id=employee_id)
            Leave.objects.create(
                employee=employee,
                leave_type=leave_type.upper(),
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='PENDING'
            )
            return redirect('attendance:leave_list')
        except Exception as e:
            # Handle error
            pass
    
    employees = Employee.objects.all().select_related('user')
    context = {'employees': employees}
    return render(request, 'attendance/leave_form.html', context)


@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    context = {'leave': leave}
    return render(request, 'attendance/leave_detail.html', context)


@login_required
def leave_approve(request, pk):
    if request.method == 'POST':
        leave = get_object_or_404(Leave, pk=pk)
        leave.status = 'APPROVED'
        leave.approved_by = request.user.get_full_name() or request.user.username
        leave.save()
        return redirect('attendance:leave_list')
    return redirect('attendance:leave_list')


@login_required
def leave_reject(request, pk):
    if request.method == 'POST':
        leave = get_object_or_404(Leave, pk=pk)
        leave.status = 'REJECTED'
        leave.approved_by = request.user.get_full_name() or request.user.username
        leave.save()
        return redirect('attendance:leave_list')
    return redirect('attendance:leave_list')


@login_required
def shift_list(request):
    shifts = Shift.objects.all()
    
    # Calculate employee count per shift
    shift_data = []
    for shift in shifts:
        employee_count = EmployeeShift.objects.filter(
            shift=shift,
            is_current=True
        ).count()
        
        shift_data.append({
            'shift': shift,
            'employee_count': employee_count
        })
    
    # Total shifts
    total_shifts = shifts.count()
    
    context = {
        'shifts': shifts,
        'shift_data': shift_data,
        'total_shifts': total_shifts,
    }
    return render(request, 'attendance/shift_list.html', context)
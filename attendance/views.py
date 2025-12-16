# attendance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Attendance, Leave, Shift

@login_required
def attendance_dashboard(request):
    today = timezone.now().date()
    attendances = Attendance.objects.filter(date=today).select_related('employee__user')
    context = {
        'attendances': attendances,
        'today': today,
        'total_present': attendances.filter(status='PRESENT').count(),
        'total_absent': attendances.filter(status='ABSENT').count(),
    }
    return render(request, 'attendance/attendance_dashboard.html', context)

@login_required
def mark_attendance(request):
    return render(request, 'attendance/mark_attendance.html')

@login_required
def attendance_report(request):
    attendances = Attendance.objects.all().select_related('employee__user')
    return render(request, 'attendance/attendance_report.html', {'attendances': attendances})

@login_required
def on_duty_list(request):
    today = timezone.now().date()
    on_duty = Attendance.objects.filter(date=today, status='PRESENT').select_related('employee__user')
    context = {'on_duty': on_duty, 'today': today}
    return render(request, 'attendance/on_duty_list.html', context)

@login_required
def leave_list(request):
    leaves = Leave.objects.all().select_related('employee__user')
    return render(request, 'attendance/leave_list.html', {'leaves': leaves})

@login_required
def leave_create(request):
    return render(request, 'attendance/leave_form.html')

@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    return render(request, 'attendance/leave_detail.html', {'leave': leave})

@login_required
def leave_approve(request, pk):
    if request.method == 'POST':
        leave = get_object_or_404(Leave, pk=pk)
        leave.status = 'APPROVED'
        leave.save()
        return redirect('attendance:leave_detail', pk=pk)
    return redirect('attendance:leave_list')

@login_required
def leave_reject(request, pk):
    if request.method == 'POST':
        leave = get_object_or_404(Leave, pk=pk)
        leave.status = 'REJECTED'
        leave.save()
        return redirect('attendance:leave_detail', pk=pk)
    return redirect('attendance:leave_list')

@login_required
def shift_list(request):
    shifts = Shift.objects.all()
    return render(request, 'attendance/shift_list.html', {'shifts': shifts})



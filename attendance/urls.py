from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Attendance Management
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('on-duty/', views.on_duty_list, name='on_duty_list'),
    
    # Leave Management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/create/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leaves/<int:pk>/approve/', views.leave_approve, name='leave_approve'),
    path('leaves/<int:pk>/reject/', views.leave_reject, name='leave_reject'),
    
    # Shift Management
    path('shifts/', views.shift_list, name='shift_list'),
]
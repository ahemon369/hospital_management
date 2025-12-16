from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('appointments/daily/', views.daily_appointments_report, name='daily_appointments_report'),
    path('billing/daily/', views.daily_billing_report, name='daily_billing_report'),
    path('medicine/stock/', views.medicine_stock_report, name='medicine_stock_report'),
    path('doctors/appointments/', views.doctor_appointments_report, name='doctor_appointments_report'),
    path('export/pdf/<str:report_type>/', views.export_report_pdf, name='export_report_pdf'),
    path('export/excel/<str:report_type>/', views.export_report_excel, name='export_report_excel'),
    path('export/csv/<str:report_type>/', views.export_report_csv, name='export_report_csv'),
]
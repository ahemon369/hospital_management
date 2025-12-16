from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee Management
    path('', views.employee_list, name='employee_list'),
    path('create/', views.employee_create, name='employee_create'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('<int:pk>/update/', views.employee_update, name='employee_update'),
    path('<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Salary Management
    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/create/', views.salary_create, name='salary_create'),
    path('salaries/<int:pk>/', views.salary_detail, name='salary_detail'),
    path('salaries/<int:pk>/pay/', views.salary_pay, name='salary_pay'),
]
# employees/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employee, Salary

@login_required
def employee_list(request):
    employees = Employee.objects.all().select_related('user')
    context = {'employees': employees}
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'employee': employee})

@login_required
def employee_create(request):
    return render(request, 'employees/employee_form.html', {'is_update': False})

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_form.html', {'employee': employee, 'is_update': True})

@login_required
def employee_delete(request, pk):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employees:employee_list')
    return redirect('employees:employee_list')

@login_required
def salary_list(request):
    salaries = Salary.objects.all().select_related('employee__user')
    context = {'salaries': salaries}
    return render(request, 'employees/salary_list.html', context)

@login_required
def salary_create(request):
    return render(request, 'employees/salary_form.html')

@login_required
def salary_detail(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    return render(request, 'employees/salary_detail.html', {'salary': salary})

@login_required
def salary_pay(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        salary.amount_paid += float(amount)
        salary.save()
        messages.success(request, 'Payment recorded successfully!')
    return redirect('employees:salary_detail', pk=pk)

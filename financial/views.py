from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Account, Transaction, Budget, Expense

@login_required
def financial_dashboard(request):
    """Financial Dashboard"""
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Get all accounts
    accounts = Account.objects.filter(status='active')
    
    # Calculate total balance
    total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
    
    # Get monthly income and expenses
    monthly_income = Transaction.objects.filter(
        transaction_type='income',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expenses = Transaction.objects.filter(
        transaction_type='expense',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate net income
    net_income = monthly_income - monthly_expenses
    
    # Get recent transactions
    recent_transactions = Transaction.objects.all().order_by('-date')[:10]
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'net_income': net_income,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'financial/financial_dashboard.html', context)

@login_required
def account_list(request):
    """List all accounts"""
    accounts = Account.objects.all().order_by('-created_at')
    return render(request, 'financial/account_list.html', {'accounts': accounts})

@login_required
def account_create(request):
    """Create new account"""
    if request.method == 'POST':
        # Handle account creation
        messages.success(request, 'Account created successfully!')
        return redirect('financial:account_list')
    
    return render(request, 'financial/account_form.html')

@login_required
def account_detail(request, pk):
    """Account detail view"""
    account = get_object_or_404(Account, pk=pk)
    transactions = Transaction.objects.filter(account=account).order_by('-date')[:20]
    
    context = {
        'account': account,
        'transactions': transactions,
    }
    
    return render(request, 'financial/account_detail.html', context)

@login_required
def transaction_list(request):
    """List all transactions"""
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'financial/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_create(request):
    """Create new transaction"""
    if request.method == 'POST':
        # Handle transaction creation
        messages.success(request, 'Transaction recorded successfully!')
        return redirect('financial:transaction_list')
    
    accounts = Account.objects.filter(status='active')
    return render(request, 'financial/transaction_form.html', {'accounts': accounts})

@login_required
def transaction_detail(request, pk):
    """Transaction detail view"""
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'financial/transaction_detail.html', {'transaction': transaction})

@login_required
def expense_list(request):
    """List all expenses"""
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'financial/expense_list.html', {'expenses': expenses})

@login_required
def expense_create(request):
    """Create new expense"""
    if request.method == 'POST':
        # Handle expense creation
        messages.success(request, 'Expense recorded successfully!')
        return redirect('financial:expense_list')
    
    return render(request, 'financial/expense_form.html')

@login_required
def budget_list(request):
    """List all budgets"""
    budgets = Budget.objects.all().order_by('-year', '-month')
    return render(request, 'financial/budget_list.html', {'budgets': budgets})

@login_required
def budget_create(request):
    """Create new budget"""
    if request.method == 'POST':
        # Handle budget creation
        messages.success(request, 'Budget created successfully!')
        return redirect('financial:budget_list')
    
    return render(request, 'financial/budget_form.html')
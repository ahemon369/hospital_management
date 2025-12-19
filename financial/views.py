from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Account, Transaction, Budget, Expense

@login_required
def financial_dashboard(request):
    """Financial Dashboard with Real Data"""
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Get all active accounts
    accounts = Account.objects.filter(status='ACTIVE')
    
    # Calculate total balance from all accounts
    total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
    
    # Get monthly income (current month)
    monthly_income = Transaction.objects.filter(
        transaction_type='INCOME',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get monthly expenses (current month)
    monthly_expenses = Transaction.objects.filter(
        transaction_type='EXPENSE',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate net income
    net_income = monthly_income - monthly_expenses
    
    # Get recent transactions (last 10)
    recent_transactions = Transaction.objects.select_related('account').order_by('-date', '-created_at')[:10]
    
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
    """List all accounts with real data"""
    accounts = Account.objects.all().order_by('-created_at')
    
    # Calculate statistics
    total_accounts = accounts.count()
    total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
    
    # Count by account type
    checking_accounts = accounts.filter(account_type='BANK').count()
    savings_accounts = accounts.filter(account_type='MOBILE_BANKING').count()
    cash_accounts = accounts.filter(account_type='CASH').count()
    
    context = {
        'accounts': accounts,
        'total_accounts': total_accounts,
        'total_balance': total_balance,
        'checking_accounts': checking_accounts,
        'savings_accounts': savings_accounts,
        'cash_accounts': cash_accounts,
    }
    
    return render(request, 'financial/account_list.html', context)

@login_required
def account_create(request):
    """Create new account"""
    if request.method == 'POST':
        # Get form data
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        account_type = request.POST.get('account_type')
        balance = request.POST.get('balance', 0)
        bank_name = request.POST.get('bank_name', '')
        branch_name = request.POST.get('branch_name', '')
        status = request.POST.get('status', 'ACTIVE')
        
        # Create account
        Account.objects.create(
            account_name=account_name,
            account_number=account_number,
            account_type=account_type,
            balance=balance,
            bank_name=bank_name,
            branch=branch_name,
            status=status
        )
        
        messages.success(request, f'Account "{account_name}" created successfully!')
        return redirect('financial:account_list')
    
    return render(request, 'financial/account_form.html')

@login_required
def account_detail(request, pk):
    """Account detail view with transactions"""
    account = get_object_or_404(Account, pk=pk)
    
    # Get all transactions for this account
    transactions = Transaction.objects.filter(account=account).order_by('-date', '-created_at')
    
    # Calculate statistics
    total_income = transactions.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    transaction_count = transactions.count()
    
    context = {
        'account': account,
        'transactions': transactions[:20],  # Last 20 transactions
        'total_income': total_income,
        'total_expense': total_expense,
        'transaction_count': transaction_count,
    }
    
    return render(request, 'financial/account_detail.html', context)

@login_required
def transaction_list(request):
    """List all transactions with real data"""
    transactions = Transaction.objects.select_related('account').order_by('-date', '-created_at')
    
    # Get current month data
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Calculate statistics
    monthly_income = transactions.filter(
        transaction_type='INCOME',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expense = transactions.filter(
        transaction_type='EXPENSE',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    net_income = monthly_income - monthly_expense
    total_transactions = transactions.count()
    
    context = {
        'transactions': transactions,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'net_income': net_income,
        'total_transactions': total_transactions,
    }
    
    return render(request, 'financial/transaction_list.html', context)

@login_required
def transaction_create(request):
    """Create new transaction"""
    if request.method == 'POST':
        # Get form data
        transaction_id = request.POST.get('transaction_id') or f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}"
        account_id = request.POST.get('account')
        transaction_type = request.POST.get('transaction_type')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'CASH')
        description = request.POST.get('description')
        reference = request.POST.get('reference_number', '')
        date = request.POST.get('date')
        
        # Get account
        account = Account.objects.get(pk=account_id)
        
        # Create transaction
        Transaction.objects.create(
            transaction_id=transaction_id,
            account=account,
            transaction_type=transaction_type.upper(),
            category=category.upper(),
            amount=amount,
            payment_method=payment_method,
            description=description,
            reference=reference,
            date=date
        )
        
        messages.success(request, f'Transaction {transaction_id} recorded successfully!')
        return redirect('financial:transaction_list')
    
    # Get active accounts for form
    accounts = Account.objects.filter(status='ACTIVE')
    return render(request, 'financial/transaction_form.html', {'accounts': accounts})

@login_required
def transaction_detail(request, pk):
    """Transaction detail view"""
    transaction = get_object_or_404(Transaction.objects.select_related('account'), pk=pk)
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'financial/transaction_detail.html', context)

@login_required
def expense_list(request):
    """List all expenses with real data"""
    expenses = Expense.objects.all().order_by('-date', '-created_at')
    
    # Calculate statistics
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    monthly_expenses = expenses.filter(
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    expense_count = expenses.count()
    
    context = {
        'expenses': expenses,
        'monthly_expenses': monthly_expenses,
        'total_expenses': total_expenses,
        'expense_count': expense_count,
    }
    
    return render(request, 'financial/expense_list.html', context)

@login_required
def expense_create(request):
    """Create new expense"""
    if request.method == 'POST':
        # Get form data
        expense_id = request.POST.get('expense_id') or f"EXP{timezone.now().strftime('%Y%m%d%H%M%S')}"
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        paid_to = request.POST.get('paid_to')
        payment_method = request.POST.get('payment_method', 'CASH')
        description = request.POST.get('description')
        date = request.POST.get('date')
        receipt_number = request.POST.get('receipt_number', '')
        
        # Create expense
        Expense.objects.create(
            expense_id=expense_id,
            category=category.upper(),
            amount=amount,
            paid_to=paid_to,
            payment_method=payment_method,
            description=description,
            date=date,
            receipt_number=receipt_number
        )
        
        messages.success(request, f'Expense {expense_id} recorded successfully!')
        return redirect('financial:expense_list')
    
    return render(request, 'financial/expense_form.html')

@login_required
def budget_list(request):
    """List all budgets with real data"""
    budgets = Budget.objects.all().order_by('-month')
    
    # Calculate statistics
    total_allocated = budgets.aggregate(total=Sum('allocated_amount'))['total'] or 0
    total_spent = budgets.aggregate(total=Sum('spent_amount'))['total'] or 0
    total_remaining = total_allocated - total_spent
    
    context = {
        'budgets': budgets,
        'total_allocated': total_allocated,
        'total_spent': total_spent,
        'total_remaining': total_remaining,
    }
    
    return render(request, 'financial/budget_list.html', context)

@login_required
def budget_create(request):
    """Create new budget"""
    if request.method == 'POST':
        # Get form data
        category = request.POST.get('category')
        month = request.POST.get('month')
        allocated_amount = request.POST.get('allocated_amount')
        notes = request.POST.get('notes', '')
        
        # Create budget
        Budget.objects.create(
            category=category.upper(),
            month=month,
            allocated_amount=allocated_amount,
            notes=notes
        )
        
        messages.success(request, 'Budget created successfully!')
        return redirect('financial:budget_list')
    
    return render(request, 'financial/budget_form.html')
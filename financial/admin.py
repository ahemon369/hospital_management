# financial/admin.py
from django.contrib import admin
from .models import Account, Transaction, Budget, Expense

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'account_name', 'account_type', 'balance', 'status']
    list_filter = ['account_type', 'status']
    search_fields = ['account_number', 'account_name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'account', 'transaction_type', 'category', 'amount', 'date']
    list_filter = ['transaction_type', 'category', 'date']
    search_fields = ['transaction_id', 'reference']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'month', 'allocated_amount', 'spent_amount', 'remaining_amount', 'utilization_percentage']
    list_filter = ['category', 'month']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expense_id', 'category', 'amount', 'paid_to', 'date']
    list_filter = ['category', 'date']
    search_fields = ['expense_id', 'paid_to']
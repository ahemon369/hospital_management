from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse
from .models import Bill
from patients.models import Patient

@login_required
def bill_list(request):
    """Display list of all bills with search and filter"""
    bills = Bill.objects.all().select_related('patient__user').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        bills = bills.filter(
            Q(bill_number__icontains=search_query) |
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(patient__patient_id__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        bills = bills.filter(status=status_filter)
    
    # Calculate statistics
    total_revenue = Bill.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    paid_bills = Bill.objects.filter(status='PAID').count()
    unpaid_bills = Bill.objects.filter(status='UNPAID').count()
    partial_bills = Bill.objects.filter(status='PARTIAL').count()
    total_bills = Bill.objects.count()
    
    context = {
        'bills': bills,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_revenue': total_revenue,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
        'partial_bills': partial_bills,
        'total_bills': total_bills,
    }
    return render(request, 'billing/bill_list.html', context)


@login_required
def bill_detail(request, pk):
    """Display detailed view of a single bill"""
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'billing/bill_detail.html', {'bill': bill})


@login_required
def bill_create(request):
    """Create a new bill with optional payment"""
    if request.method == 'POST':
        try:
            # Get patient
            patient_id = request.POST.get('patient')
            if not patient_id:
                messages.error(request, 'Please select a patient!')
                patients = Patient.objects.all().select_related('user')
                return render(request, 'billing/bill_form.html', {
                    'patients': patients,
                    'is_update': False
                })
            
            patient = get_object_or_404(Patient, pk=patient_id)
            
            # Get amounts
            consultation_fee = float(request.POST.get('consultation_fee') or 0)
            medicine_charges = float(request.POST.get('medicine_charges') or 0)
            lab_charges = float(request.POST.get('lab_charges') or 0)
            other_charges = float(request.POST.get('other_charges') or 0)
            discount = float(request.POST.get('discount') or 0)
            tax = float(request.POST.get('tax') or 0)
            notes = request.POST.get('notes', '').strip()
            
            # Get payment information
            amount_paid = float(request.POST.get('amount_paid') or 0)
            payment_method = request.POST.get('payment_method', '').strip()
            
            # Calculate total
            subtotal = consultation_fee + medicine_charges + lab_charges + other_charges
            total_amount = subtotal - discount + tax
            
            # Validate total
            if total_amount <= 0:
                messages.error(request, 'Bill total must be greater than zero!')
                patients = Patient.objects.all().select_related('user')
                return render(request, 'billing/bill_form.html', {
                    'patients': patients,
                    'is_update': False
                })
            
            # Validate payment
            if amount_paid > total_amount:
                messages.error(request, 'Amount paid cannot exceed total amount!')
                patients = Patient.objects.all().select_related('user')
                return render(request, 'billing/bill_form.html', {
                    'patients': patients,
                    'is_update': False
                })
            
            # Determine status based on payment
            if amount_paid == 0:
                status = 'UNPAID'
            elif amount_paid >= total_amount:
                status = 'PAID'
            else:
                status = 'PARTIAL'
            
            # Add payment info to notes if payment received
            if payment_method and amount_paid > 0:
                payment_note = f"\n\n--- Initial Payment ---\nMethod: {payment_method}\nAmount: ৳{amount_paid:.2f}"
                notes = (notes + payment_note) if notes else payment_note.strip()
            
            # Create bill
            bill = Bill.objects.create(
                patient=patient,
                consultation_fee=consultation_fee,
                medicine_charges=medicine_charges,
                lab_charges=lab_charges,
                other_charges=other_charges,
                discount=discount,
                tax=tax,
                total_amount=total_amount,
                amount_paid=amount_paid,
                balance=total_amount - amount_paid,
                notes=notes,
                status=status
            )
            
            # Success message
            status_msg = f"Status: {bill.get_status_display()}"
            if amount_paid > 0:
                status_msg += f" (৳{amount_paid:.2f} paid)"
            
            messages.success(request, f'Bill {bill.bill_number} created successfully! {status_msg}')
            return redirect('billing:bill_detail', pk=bill.pk)
            
        except ValueError:
            messages.error(request, 'Invalid amount entered. Please check your inputs.')
            patients = Patient.objects.all().select_related('user')
            return render(request, 'billing/bill_form.html', {
                'patients': patients,
                'is_update': False
            })
        except Exception as e:
            messages.error(request, f'Error creating bill: {str(e)}')
            patients = Patient.objects.all().select_related('user')
            return render(request, 'billing/bill_form.html', {
                'patients': patients,
                'is_update': False
            })
    
    # GET request - show form
    patients = Patient.objects.all().select_related('user')
    context = {
        'patients': patients,
        'is_update': False
    }
    return render(request, 'billing/bill_form.html', context)


@login_required
def bill_update(request, pk):
    """Update an existing bill"""
    bill = get_object_or_404(Bill, pk=pk)
    
    if request.method == 'POST':
        try:
            # Get amounts
            consultation_fee = float(request.POST.get('consultation_fee') or 0)
            medicine_charges = float(request.POST.get('medicine_charges') or 0)
            lab_charges = float(request.POST.get('lab_charges') or 0)
            other_charges = float(request.POST.get('other_charges') or 0)
            discount = float(request.POST.get('discount') or 0)
            tax = float(request.POST.get('tax') or 0)
            notes = request.POST.get('notes', '').strip()
            
            # Calculate total
            subtotal = consultation_fee + medicine_charges + lab_charges + other_charges
            total_amount = subtotal - discount + tax
            
            # Validate
            if total_amount <= 0:
                messages.error(request, 'Bill total must be greater than zero!')
                patients = Patient.objects.all().select_related('user')
                return render(request, 'billing/bill_form.html', {
                    'bill': bill,
                    'patients': patients,
                    'is_update': True
                })
            
            # Update bill fields
            bill.consultation_fee = consultation_fee
            bill.medicine_charges = medicine_charges
            bill.lab_charges = lab_charges
            bill.other_charges = other_charges
            bill.discount = discount
            bill.tax = tax
            bill.total_amount = total_amount
            bill.notes = notes
            
            # Save (model's save() method will update balance and status)
            bill.save()
            
            messages.success(request, f'Bill {bill.bill_number} updated successfully!')
            return redirect('billing:bill_detail', pk=bill.pk)
            
        except ValueError:
            messages.error(request, 'Invalid amount entered. Please check your inputs.')
        except Exception as e:
            messages.error(request, f'Error updating bill: {str(e)}')
    
    # GET request - show form with bill data
    patients = Patient.objects.all().select_related('user')
    context = {
        'bill': bill,
        'patients': patients,
        'is_update': True
    }
    return render(request, 'billing/bill_form.html', context)


@login_required
def bill_delete(request, pk):
    """Delete a bill"""
    bill = get_object_or_404(Bill, pk=pk)
    
    if request.method == 'POST':
        bill_number = bill.bill_number
        bill.delete()
        messages.success(request, f'Bill {bill_number} deleted successfully!')
        return redirect('billing:bill_list')
    
    # If not POST, redirect to detail page
    return redirect('billing:bill_detail', pk=pk)


@login_required
def record_payment(request, pk):
    """Record a payment for a bill"""
    bill = get_object_or_404(Bill, pk=pk)
    
    if request.method == 'POST':
        try:
            payment_amount = float(request.POST.get('payment_amount', 0))
            
            # Validate payment amount
            if payment_amount <= 0:
                messages.error(request, 'Payment amount must be greater than zero!')
                return redirect('billing:bill_detail', pk=pk)
            
            if payment_amount > bill.balance:
                messages.error(request, f'Payment amount cannot exceed balance due of ৳{bill.balance:.2f}!')
                return redirect('billing:bill_detail', pk=pk)
            
            # Update payment
            bill.amount_paid += payment_amount
            
            # Save (model's save() method will update balance and status automatically)
            bill.save()
            
            messages.success(request, f'Payment of ৳{payment_amount:.2f} recorded successfully! New status: {bill.get_status_display()}')
            
        except ValueError:
            messages.error(request, 'Invalid payment amount!')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
    
    return redirect('billing:bill_detail', pk=pk)


@login_required
def bill_pdf(request, pk):
    """Generate PDF for a bill"""
    bill = get_object_or_404(Bill, pk=pk)
    
    # Simple PDF response (you can enhance this with reportlab or weasyprint later)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="bill_{bill.bill_number}.pdf"'
    
    # Basic PDF content
    pdf_content = f"""
%PDF-1.4

===============================================
    HOSPITAL MANAGEMENT SYSTEM
    BILL INVOICE
===============================================

Bill Number: {bill.bill_number}
Date: {bill.created_at.strftime('%B %d, %Y')}
Status: {bill.get_status_display()}

-----------------------------------------------
PATIENT INFORMATION
-----------------------------------------------
Name: {bill.patient.get_full_name()}
Patient ID: {bill.patient.patient_id}
Email: {bill.patient.user.email}

-----------------------------------------------
BILL DETAILS
-----------------------------------------------
Consultation Fee:       ৳{bill.consultation_fee:.2f}
Medicine Charges:       ৳{bill.medicine_charges:.2f}
Lab Charges:           ৳{bill.lab_charges:.2f}
Other Charges:         ৳{bill.other_charges:.2f}

Subtotal:              ৳{bill.subtotal:.2f}
Discount:              -৳{bill.discount:.2f}
Tax:                   +৳{bill.tax:.2f}

-----------------------------------------------
TOTAL AMOUNT:          ৳{bill.total_amount:.2f}
AMOUNT PAID:           ৳{bill.amount_paid:.2f}
BALANCE DUE:           ৳{bill.balance:.2f}
-----------------------------------------------

Notes: 
{bill.notes or 'N/A'}

-----------------------------------------------
Generated on: {bill.updated_at.strftime('%B %d, %Y at %I:%M %p')}
===============================================
"""
    
    response.write(pdf_content.encode('utf-8'))
    return response
@login_required
def bill_pdf(request, pk):
    """Generate PDF invoice for a bill"""
    bill = get_object_or_404(Bill, pk=pk)
    
    # Render the invoice template
    return render(request, 'billing/bill_invoice.html', {'bill': bill})
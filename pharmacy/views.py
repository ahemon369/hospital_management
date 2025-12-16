from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import Medicine

@login_required
def medicine_list(request):
    """Display list of all medicines"""
    medicines = Medicine.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        medicines = medicines.filter(
            Q(medicine_id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )
    
    # Low stock medicines
    low_stock = medicines.filter(stock_quantity__lte=F('reorder_level'))
    
    context = {
        'medicines': medicines,
        'search_query': search_query,
        'total_medicines': Medicine.objects.count(),
        'low_stock_count': low_stock.count(),
        'low_stock_medicines': low_stock[:5],
    }
    return render(request, 'pharmacy/medicine_list.html', context)


@login_required
def medicine_detail(request, pk):
    """Display detailed view of a medicine"""
    medicine = get_object_or_404(Medicine, pk=pk)
    return render(request, 'pharmacy/medicine_detail.html', {'medicine': medicine})


@login_required
def medicine_create(request):
    """Create a new medicine"""
    if request.method == 'POST':
        try:
            # Get form data
            medicine_id = request.POST.get('medicine_id', '').strip()
            name = request.POST.get('name', '').strip()
            category = request.POST.get('category', '').strip()
            manufacturer = request.POST.get('manufacturer', '').strip()
            description = request.POST.get('description', '').strip()
            stock_quantity = int(request.POST.get('stock_quantity', 0))
            unit = request.POST.get('unit', '').strip()
            expiry_date = request.POST.get('expiry_date')
            purchase_price = float(request.POST.get('purchase_price', 0))
            selling_price = float(request.POST.get('selling_price', 0))
            reorder_level = int(request.POST.get('reorder_level', 10))
            
            # Validate required fields
            if not all([medicine_id, name, category, manufacturer, unit, expiry_date]):
                messages.error(request, 'All required fields must be filled!')
                return render(request, 'pharmacy/medicine_form.html', {
                    'is_update': False
                })
            
            # Check if medicine_id already exists
            if Medicine.objects.filter(medicine_id=medicine_id).exists():
                messages.error(request, f'Medicine ID "{medicine_id}" already exists!')
                return render(request, 'pharmacy/medicine_form.html', {
                    'is_update': False
                })
            
            # Validate prices
            if purchase_price < 0 or selling_price < 0:
                messages.error(request, 'Prices cannot be negative!')
                return render(request, 'pharmacy/medicine_form.html', {
                    'is_update': False
                })
            
            if selling_price < purchase_price:
                messages.warning(request, 'Selling price is less than purchase price!')
            
            # Create medicine
            medicine = Medicine.objects.create(
                medicine_id=medicine_id,
                name=name,
                category=category,
                manufacturer=manufacturer,
                description=description,
                stock_quantity=stock_quantity,
                unit=unit,
                expiry_date=expiry_date,
                purchase_price=purchase_price,
                selling_price=selling_price,
                reorder_level=reorder_level
            )
            
            messages.success(request, f'Medicine "{medicine.name}" added successfully!')
            return redirect('pharmacy:medicine_detail', pk=medicine.pk)
            
        except ValueError as e:
            messages.error(request, 'Invalid number format. Please check quantity and prices.')
            return render(request, 'pharmacy/medicine_form.html', {
                'is_update': False
            })
        except Exception as e:
            messages.error(request, f'Error adding medicine: {str(e)}')
            return render(request, 'pharmacy/medicine_form.html', {
                'is_update': False
            })
    
    # GET request - show form
    context = {
        'is_update': False
    }
    return render(request, 'pharmacy/medicine_form.html', context)


@login_required
def medicine_update(request, pk):
    """Update an existing medicine"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            category = request.POST.get('category', '').strip()
            manufacturer = request.POST.get('manufacturer', '').strip()
            description = request.POST.get('description', '').strip()
            stock_quantity = int(request.POST.get('stock_quantity', 0))
            unit = request.POST.get('unit', '').strip()
            expiry_date = request.POST.get('expiry_date')
            purchase_price = float(request.POST.get('purchase_price', 0))
            selling_price = float(request.POST.get('selling_price', 0))
            reorder_level = int(request.POST.get('reorder_level', 10))
            
            # Validate required fields
            if not all([name, category, manufacturer, unit, expiry_date]):
                messages.error(request, 'All required fields must be filled!')
                return render(request, 'pharmacy/medicine_form.html', {
                    'medicine': medicine,
                    'is_update': True
                })
            
            # Update medicine
            medicine.name = name
            medicine.category = category
            medicine.manufacturer = manufacturer
            medicine.description = description
            medicine.stock_quantity = stock_quantity
            medicine.unit = unit
            medicine.expiry_date = expiry_date
            medicine.purchase_price = purchase_price
            medicine.selling_price = selling_price
            medicine.reorder_level = reorder_level
            
            medicine.save()
            
            messages.success(request, f'Medicine "{medicine.name}" updated successfully!')
            return redirect('pharmacy:medicine_detail', pk=medicine.pk)
            
        except ValueError:
            messages.error(request, 'Invalid number format. Please check quantity and prices.')
        except Exception as e:
            messages.error(request, f'Error updating medicine: {str(e)}')
    
    # GET request - show form with medicine data
    context = {
        'medicine': medicine,
        'is_update': True
    }
    return render(request, 'pharmacy/medicine_form.html', context)


@login_required
def medicine_delete(request, pk):
    """Delete a medicine"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        medicine_name = medicine.name
        medicine.delete()
        messages.success(request, f'Medicine "{medicine_name}" deleted successfully!')
        return redirect('pharmacy:medicine_list')
    
    return redirect('pharmacy:medicine_detail', pk=pk)


@login_required
def update_stock(request, pk):
    """Update medicine stock"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')  # 'add' or 'remove'
            quantity = int(request.POST.get('quantity', 0))
            
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than zero!')
                return redirect('pharmacy:medicine_detail', pk=pk)
            
            if action == 'add':
                medicine.stock_quantity += quantity
                messages.success(request, f'Added {quantity} {medicine.unit} to stock!')
            elif action == 'remove':
                if medicine.stock_quantity < quantity:
                    messages.error(request, 'Insufficient stock quantity!')
                    return redirect('pharmacy:medicine_detail', pk=pk)
                medicine.stock_quantity -= quantity
                messages.success(request, f'Removed {quantity} {medicine.unit} from stock!')
            
            medicine.save()
            
        except ValueError:
            messages.error(request, 'Invalid quantity!')
        except Exception as e:
            messages.error(request, f'Error updating stock: {str(e)}')
    
    return redirect('pharmacy:medicine_detail', pk=pk)
# suppliers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Supplier, PurchaseOrder

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'suppliers/supplier_detail.html', {'supplier': supplier})

@login_required
def supplier_create(request):
    return render(request, 'suppliers/supplier_form.html')

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'suppliers/supplier_form.html', {'supplier': supplier})

@login_required
def supplier_delete(request, pk):
    if request.method == 'POST':
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.delete()
        return redirect('suppliers:supplier_list')
    return redirect('suppliers:supplier_list')

@login_required
def purchase_order_list(request):
    orders = PurchaseOrder.objects.all().select_related('supplier')
    return render(request, 'suppliers/purchase_order_list.html', {'orders': orders})

@login_required
def purchase_order_create(request):
    return render(request, 'suppliers/purchase_order_form.html')

@login_required
def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'suppliers/purchase_order_detail.html', {'order': order})

@login_required
def purchase_order_update(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'suppliers/purchase_order_form.html', {'order': order})

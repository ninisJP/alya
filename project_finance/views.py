from django.shortcuts import render
from accounting_order_sales.models import PurchaseOrder, CollectionOrders, PurchaseOrderItem
from django.db.models import Sum

def dashboard(request):
    """
    Calculamos los totales de compras, ventas, cuentas por pagar y cobrar
    """
    accounts_payable = PurchaseOrderItem.objects.filter(payment_status='No Pagado').aggregate(total=Sum('price_total'))['total'] or 0# Cuentas por pagar
    accounts_receivable = CollectionOrders.objects.aggregate(total=Sum('monto_neto_cobrar'))['total'] or 0 # Cuentas por cobrar
    total_purchases = PurchaseOrderItem.objects.filter(payment_status='Pagado').aggregate(total=Sum('price_total'))['total'] or 0 # Total compras
    total_sales = CollectionOrders.objects.filter(factura_pagado=True).aggregate(total=Sum('monto_neto_cobrar'))['total'] or 0 # Total ventas
    total_income = total_sales # Total ingresos
    total_expenses = PurchaseOrderItem.objects.all().aggregate(total=Sum('price_total'))['total'] or 0 # Total egresos
    total_utility = total_income - total_expenses # Total utilidad

    context = {
            'accounts_payable' : accounts_payable,
            'accounts_receivable' : accounts_receivable,
            'total_purchases' : total_purchases,
            'total_sales' : total_sales,
            'total_income' : total_income,
            'total_expenses' : total_expenses,
            'total_utility' : total_utility
        }

    return render(request, 'dashboard.html', context)

def accounts_payable_detail(request):# Cuentas por pagar
    items = PurchaseOrderItem.objects.filter(payment_status='No Pagado')
    context = {'items': items}
    return render(request, 'partials/accounts_payable_detail.html', context)

def accounts_receivable_detail(request):# Cuentas por cobrar
    details = CollectionOrders.objects.all() 
    context = {'details': details}
    return render(request, 'partials/accounts_receivable_detail.html', context)

def total_purchases_detail(request):# Total Compras
    details = PurchaseOrder.objects.all() 
    context = {'details': details}
    return render(request, 'partials/total_purchases_detail.html', context)

def total_sales_detail(request):# Total Ventas
    details = PurchaseOrder.objects.all() 
    context = {'details': details}
    return render(request, 'partials/total_sales_detail.html', context)

def total_income_detail(request):# Total Ingresos
    details = PurchaseOrder.objects.all() 
    context = {'details': details}
    return render(request, 'partials/total_income_detail.html', context)

def total_expenses_detail(request):# Total Egresos
    details = PurchaseOrder.objects.all() 
    context = {'details': details}
    return render(request, 'partials/total_expenses_detail.html', context)

from django.db.models import Sum
from django.shortcuts import render

from accounting_order_sales import models as accounting_order_sales_models
from accounting_order_sales.models import PurchaseOrder, CollectionOrders, PurchaseOrderItem

from . import utils



def dashboard(request):
    """
    Calculamos los totales de compras, ventas, cuentas por pagar y cobrar
    """
    context = {}

    # Finances calculate
    context_all = utils.calculate_all()
    context.update(context_all)

    return render(request, 'dashboard.html', context)

def accounts_payable_detail(request):# Cuentas por pagar
    #items = PurchaseOrderItem.objects.filter(payment_status='No Pagado')
    loans = accounting_order_sales_models.BankLoan.objects.all()
    collections = accounting_order_sales_models.CollectionOrders.objects.all()

    context = {}
    context['loans'] = loans
    context['collections '] = collections

    return render(request, 'partials/accounts_payable_detail.html', context)

def accounts_receivable_detail(request):# Cuentas por cobrar
    context = utils.get_model_receivable()
    return render(request, 'partials/accounts_receivable_detail.html', context)

def total_purchases_detail(request):# Total Compras
    context = utils.get_model_purchase()
    return render(request, 'partials/total_purchases_detail.html', context)

def total_sales_detail(request):# Total Ventas
    context = utils.get_model_sale()
    return render(request, 'partials/total_sales_detail.html', context)

def total_income_detail(request):# Total Ingresos
    context = utils.get_model_income()
    return render(request, 'partials/total_income_detail.html', context)

def total_expenses_detail(request):# Total Egresos
    details = PurchaseOrder.objects.all()
    context = {'details': details}
    return render(request, 'partials/total_expenses_detail.html', context)

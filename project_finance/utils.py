# See LICENSE file for copyright and license details.
"""
Project Finance Utils
"""
from django.db.models import Sum

from accounting_order_sales import models as accounting_order_sales_models
from accounting_sunat import models as accounting_sunat_models


def calculate_all():
    """"
    Calculate all the values of the finance module
    """
    context = {}
    (
        total_income_pen,
        total_income_usd,
        context_income) = calculate_income()
    (
        total_expenses_pen,
        total_expenses_usd,
        context_expenses) = calculate_expenses()
    context_receivable = calculate_receivable()
    context_payable = calculate_payable()

    context.update(context_income)
    context.update(context_expenses)
    context.update(context_receivable)
    context.update(context_payable)
    total_utility_pen = total_income_pen - total_expenses_pen
    total_utility_usd = total_income_usd - total_expenses_usd
    context['total_utility_pen'] = total_utility_pen
    context['total_utility_usd'] = total_utility_usd

    return context


# INGRESOS
def get_model_income():
    """
    Get the model of the income
    """
    context = {}
    # pylint: disable=no-member
    loan_pen = accounting_order_sales_models.BankLoan.objects.filter(
        currency='Soles')
    # pylint: disable=no-member
    loan_usd = accounting_order_sales_models.BankLoan.objects.filter(
        currency='Dolares')
    context['income_list_pen'] = loan_pen
    context['income_list_usd'] = loan_usd

    context_sale = get_model_sale()
    context.update(context_sale)

    return context


def calculate_income():
    """"
    Calculate the income of the finance module
    """
    context = {}
    # pylint: disable=no-member
    loan_pen = accounting_order_sales_models.BankLoan.objects.filter(
        currency='Soles'
        ).aggregate(total=Sum('total_debt'))['total'] or 0
    # pylint: disable=no-member
    loan_usd = accounting_order_sales_models.BankLoan.objects.filter(
        currency='Dolares'
        ).aggregate(total=Sum('total_debt'))['total'] or 0

    # Sale
    sale_pen, sale_usd, context_sale = calculate_sale()
    # Total
    total_loan_pen = loan_pen + sale_pen
    total_loan_usd = loan_usd + sale_usd
    context.update(context_sale)
    context['total_income_pen'] = total_loan_pen
    context['total_income_usd'] = total_loan_usd

    return total_loan_pen, total_loan_usd, context


# EGRESOS
def get_model_expenses():
    """Get the model of the expenses"""
    context = {}
    list_pen = []
    list_usd = []
    # pylint: disable=no-member
    for item in accounting_order_sales_models.PartialPayment.objects.all():
        if item.loan_payment.loan.currency == "Soles":
            list_pen.append(item.pk)
        else:
            list_usd.append(item.pk)

    loan_pen = accounting_order_sales_models.PartialPayment.objects.filter(
        pk__in=list_pen)
    loan_usd = accounting_order_sales_models.PartialPayment.objects.filter(
        pk__in=list_usd)
    # Sunat
    sunat_pen = accounting_sunat_models.Pago.objects.filter(pagado=True)

    context_purchase = get_model_purchase()
    context.update(context_purchase)

    context['expense_list_pen'] = loan_pen
    context['expense_list_usd'] = loan_usd
    context['sunat_list_pen'] = sunat_pen

    return context


def calculate_expenses():
    """Calculate the expenses of the finance module"""
    context = {}
    list_pen = []
    list_usd = []
    # pylint: disable=no-member
    for item in accounting_order_sales_models.PartialPayment.objects.all():
        if item.loan_payment.loan.currency == "Soles":
            list_pen.append(item.pk)
        else:
            list_usd.append(item.pk)
            # pylint: disable=no-member
    loan_pen = accounting_order_sales_models.PartialPayment.objects.filter(
        pk__in=list_pen
        ).aggregate(total=Sum('partial_amount'))['total'] or 0
    # pylint: disable=no-member
    loan_usd = accounting_order_sales_models.PartialPayment.objects.filter(
        pk__in=list_usd
        ).aggregate(total=Sum('partial_amount'))['total'] or 0
    # pylint: disable=no-member
    sunat_pen = accounting_sunat_models.Pago.objects.filter(
        pagado=True
        ).aggregate(total=Sum('total'))['total'] or 0

    (
        total_purchase_pen,
        total_purchase_usd,
        context_purchase) = calculate_purchase()

    context.update(context_purchase)

    total_expenses_pen = loan_pen + total_purchase_pen + sunat_pen
    total_expenses_usd = loan_usd + total_purchase_usd

    context['total_expenses_pen'] = total_expenses_pen
    context['total_expenses_usd'] = total_expenses_usd

    return total_expenses_pen, total_expenses_usd, context


def get_model_sale():
    """Get the model of the sale"""
    context = {}
    # pylint: disable=no-member
    sale_pen = accounting_order_sales_models.CollectionOrders.objects.filter(
        tipo_moneda='SOLES',
        factura_pagado=True)
    # pylint: disable=no-member
    sale_usd = accounting_order_sales_models.CollectionOrders.objects.filter(
        tipo_moneda='DOLARES',
        factura_pagado=True)

    context['sale_list_pen'] = sale_pen
    context['sale_list_usd'] = sale_usd

    return context


def calculate_sale():
    """Calculate the sale of the finance module"""
    context = {}
    # pylint: disable=no-member
    sale_pen = accounting_order_sales_models.CollectionOrders.objects.filter(
        tipo_moneda='SOLES',
        factura_pagado=True
        ).aggregate(total=Sum('importe_total'))['total'] or 0
    # pylint: disable=no-member
    sale_usd = accounting_order_sales_models.CollectionOrders.objects.filter(
        tipo_moneda='DOLARES',
        factura_pagado=True
        ).aggregate(total=Sum('importe_total'))['total'] or 0
    total_sale_pen = sale_pen
    total_sale_usd = sale_usd

    context['total_sale_pen'] = total_sale_pen
    context['total_sale_usd'] = total_sale_usd

    return sale_pen, sale_usd, context


def get_model_purchase():
    """Get the model of the purchase"""
    context = {}
    # pylint: disable=no-member
    purchase_pen = (
        accounting_order_sales_models.PurchaseOrderItem.objects.filter(
            payment_status='Pagado'))
    context['purchase_list_pen'] = purchase_pen
    return context


def calculate_purchase():
    """
    Calculates and returns the purchase totals in local currency and dollars.
    Performs a query on the paid purchase order items to obtain the accumulated
    total in local currency (PEN).

    Returns
    -------
    Tuple with three elements:
    - total_purchase_pen (float): PEN currency
    - total_purchase_usd (float): USD currency
    - context (dict): Dict

    Examples
    --------
    >>> total_pen, total_usd, contexto = calculate_purchase()
    >>> print(total_pen)
    15000.50

    """
    context = {}
    # pylint: disable=no-member
    purchase_pen = (
        accounting_order_sales_models.PurchaseOrderItem.objects.filter(
            payment_status='Pagado'
            ).aggregate(total=Sum('price_total'))['total'] or 0)
    total_purchase_pen = purchase_pen
    context['total_purchase_pen'] = total_purchase_pen

    return total_purchase_pen, 0, context


# Cuentas por Cobrar
def get_model_receivable():
    """Get the model of the receivable"""
    context = {}
    # pylint: disable=no-member
    collection_pen = (
        accounting_order_sales_models.CollectionOrders.objects.filter(
            tipo_moneda='SOLES',
            factura_pagado=False))
    # pylint: disable=no-member
    collection_usd = (
        accounting_order_sales_models.CollectionOrders.objects.filter(
            tipo_moneda='DOLARES',
            factura_pagado=False))
    context['receivable_list_pen'] = collection_pen
    context['receivable_list_usd'] = collection_usd

    return context


def calculate_receivable():
    """
    Calculates and returns the receivable totals in local
    currency and dollars.
    """
    context = {}
    # pylint: disable=no-member
    collection_pen = (
        accounting_order_sales_models.CollectionOrders.objects.filter(
            tipo_moneda='SOLES',
            factura_pagado=False
            ).aggregate(total=Sum('importe_total'))['total'] or 0)
    # pylint: disable=no-member
    collection_usd = (
        accounting_order_sales_models.CollectionOrders.objects.filter(
            tipo_moneda='DOLARES',
            factura_pagado=False
            ).aggregate(total=Sum('importe_total'))['total'] or 0)

    total_receivable_pen = collection_pen
    total_receivable_usd = collection_usd
    context['total_receivable_pen'] = total_receivable_pen
    context['total_receivable_usd'] = total_receivable_usd

    return context


def get_model_payable():
    """Get the model of the payable"""
    context = {}
    # pylint: disable=no-member
    purchase_pen = (
        accounting_order_sales_models.PurchaseOrderItem.objects.filter(
            payment_status='No Pagado'))
    # pylint: disable=no-member
    sunat_pen = accounting_sunat_models.Pago.objects.filter(pagado=False)

    context['purchase_list_pen'] = purchase_pen
    context['sunat_list_pen'] = sunat_pen

    return context


def calculate_payable():
    """Calculate the payable of the finance module"""
    context = {}
    # pylint: disable=no-member
    purchase_pen = (
        accounting_order_sales_models.PurchaseOrderItem.objects.filter(
            payment_status='No Pagado'
            ).aggregate(total=Sum('price_total'))['total'] or 0)
    sunat_pen = (
        accounting_sunat_models.Pago.objects.filter(
            pagado=False
            ).aggregate(total=Sum('total'))['total'] or 0)
    total_payable_pen = purchase_pen + sunat_pen
    context['total_payable_pen'] = total_payable_pen

    return context

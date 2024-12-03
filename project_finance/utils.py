from django.db.models import Sum

from accounting_order_sales import models as accounting_order_sales_models

def calculate_all():
	context = {}

	total_income_pen, total_income_usd, context_income = calculate_income()
	total_expenses_pen, total_expenses_usd, context_expenses = calculate_expenses()

	context.update(context_income)
	context.update(context_expenses)

	total_utility_pen = total_income_pen - total_expenses_pen
	total_utility_usd = total_income_usd - total_expenses_usd

	context['total_utility_pen'] = total_utility_pen
	context['total_utility_usd'] = total_utility_usd

	return context


def calculate_income():
	context = {}

	loan_pen = accounting_order_sales_models.BankLoan.objects.filter(currency='Soles').aggregate(total=Sum('total_debt'))['total'] or 0 # Total compras
	loan_usd = accounting_order_sales_models.BankLoan.objects.filter(currency='Dolares').aggregate(total=Sum('total_debt'))['total'] or 0 # Total compras

	total_loan_pen = loan_pen
	total_loan_usd = loan_usd

	context['total_income_pen'] = total_loan_pen
	context['total_income_usd'] = total_loan_usd

	return total_loan_pen, total_loan_usd, context

def calculate_expenses():
	context = {}

	# Loan
	list_pen = []
	list_usd = []
	for item in accounting_order_sales_models.PartialPayment.objects.all() :
		if item.loan_payment.loan.currency == "Soles" :
			list_pen.append(item.pk)
		else :
			list_usd.append(item.pk)

	loan_pen = accounting_order_sales_models.PartialPayment.objects.filter(pk__in=list_pen).aggregate(total=Sum('partial_amount'))['total'] or 0
	loan_usd = accounting_order_sales_models.PartialPayment.objects.filter(pk__in=list_usd).aggregate(total=Sum('partial_amount'))['total'] or 0

	total_expenses_pen = loan_pen
	total_expenses_usd = loan_usd


	context['total_expenses_pen'] = total_expenses_pen
	context['total_expenses_usd'] = total_expenses_usd

	return total_expenses_pen, total_expenses_usd, context


from datetime import date
from dateutil.relativedelta import relativedelta

from . import models

def loan_new(form):
	# Valid debt
	total_debt = form.cleaned_data['total_debt']
	if total_debt<=0 :
		return -1, {}

	# Valid cu =oftras
	cuotas = form.cleaned_data['cuotas']
	if cuotas <=0:
		return -1, {}

	monto_cuota = total_debt/cuotas
	# Save bank load
	loan = form.save();

	original_date = loan.start_date
	# Create cuotas
	for i in range(0,cuotas):
		coute_date = original_date + relativedelta(months=i)
		load_coute = models.LoanPayment(
				loan = loan,
				amount = monto_cuota,
				pay_date = coute_date
				)
		load_coute.save()

	return 0, loan

def save_edit_coutas(form, couta):
	context = {}
	status = "no"
	form.save()

	new_amount = form.cleaned_data['amount']

	# Get all amount
	total_pay_calculate = 0
	for individual_pay in models.LoanPayment.objects.filter(loan=couta.loan):
		total_pay_calculate += individual_pay.amount

	total_pay = couta.loan.total_debt

	context['total_pay_calculate'] = total_pay_calculate
	context['total_pay'] = total_pay

	diff = abs(total_pay - total_pay_calculate)/total_pay
	# Max porcentage to variation
	context['total_pay_status'] = 0
	context['total_pay_variation'] = int(diff*100)
	if diff > 0.20 :
		status = "exceso"
		context['total_pay_status'] = 20
		return status, context
	elif diff > 0.1 :
		context['total_pay_status'] = 10

	status = "yes"
	return status, context

def classify_loan(all_models):
	context = {}
	loan_credito = all_models.filter(credit_type='credito')
	loan_prestamo = all_models.filter(credit_type='prestamo')

	list_prestamo = []
	for item in loan_prestamo :
		loan = (item.__dict__)
		payments = 0
		for pay in models.LoanPayment.objects.filter(loan=item) :
			if pay.is_paid:
				payments += 1
		loan["coutes_paid"] = payments
		list_prestamo.append(loan)

	list_credito = []
	for item in loan_credito :
		loan = (item.__dict__)
		payments = 0
		for pay in models.LoanPayment.objects.filter(loan=item) :
			if pay.is_paid:
				payments += 1
		loan["coutes_paid"] = payments
		list_credito.append(loan)

	context["loan_credito"] = list_credito
	context["loan_prestamo"] = list_prestamo
	return context

def get_no_pay(loan):
	payment = models.LoanPayment.objects.filter(loan=loan, is_paid=False)
	context = {}

	list_pay = []
	for item in payment :
		pay = (item.__dict__)
		total_pay = 0

		for individual_pay in models.PartialPayment.objects.filter(loan_payment=item):
			total_pay += individual_pay.partial_amount

		error = False
		if item.amount < total_pay :
			error = True
		pay["total"] = total_pay
		pay["error"] = error
		list_pay.append(pay)

	context["loan_cuota"] = list_pay
	return context

def get_all_pay(loan):
	payment = models.LoanPayment.objects.filter(loan=loan)
	context = {}
	list_pay = []
	for item in payment :
		pay = (item.__dict__)
		total_pay = 0
		partial = models.PartialPayment.objects.filter(loan_payment=item)
		for individual_pay in partial :
			total_pay += individual_pay.partial_amount

		error = False
		if item.amount < total_pay :
			error = True
		pay["total"] = total_pay
		pay["error"] = error

		# Get partial pay
		pay["partial"] = partial
		# Add to list
		list_pay.append(pay)

	context["loan_cuota"] = list_pay
	return context

def save_pay(form):
	status = "no"
	list_pay = []

	loan_payment = form.cleaned_data['loan_payment']
	now_payment = form.cleaned_data['partial_amount']

	total_pay = now_payment
	for individual_pay in models.PartialPayment.objects.filter(loan_payment=loan_payment):
		total_pay += individual_pay.partial_amount

	if loan_payment.amount < total_pay :
		return status

	print(form)
	print(form.cleaned_data['receipt'])
	form.save()
	# Complete pay
	if loan_payment.amount == total_pay :
		loan_payment.is_paid = True
		loan_payment.save()

	# Complete loan
	loan = loan_payment.loan
	payment_all = models.LoanPayment.objects.filter(loan=loan, is_paid=False)
	if not payment_all :
		loan.is_paid = True
		loan.save()

	status = "yes"
	return status

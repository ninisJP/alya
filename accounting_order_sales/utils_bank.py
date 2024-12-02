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

def get_all_loan():
	context = {}
	loan_credito = list(models.BankLoan.objects.filter(credit_type='credito'))
	loan_prestamo = models.BankLoan.objects.filter(credit_type='prestamo')

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

def get_all_pay(loan, all_pay=False):

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

	if all_pay:
		payment = models.LoanPayment.objects.filter(loan=loan, is_paid=True)
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

	form.save()
	# Complete
	if loan_payment.amount == total_pay :
		loan_payment.is_paid = True
		loan_payment.save()

	status = "yes"
	return status


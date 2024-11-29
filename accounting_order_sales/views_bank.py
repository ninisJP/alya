from django.shortcuts import render, get_object_or_404

from . import models
from . import forms
from . import utils_bank

def loan_main(request):
	context_items = utils_bank.get_all_loan()
	form = forms.BankLoanForm()

	context = {}
	context.update(context_items)

	context['form'] = form
	return render(request, 'bank/loan/home.html', context)

def loan_new(request):
	context = {}
	if request.method == 'POST':
		form = forms.BankLoanForm(request.POST)
		status = "no"
		if form.is_valid() :
			# Save new loan
			status_save, loan = utils_bank.loan_new(form)
			if not status_save :
				status = "yes"
			context['status'] = status

			# Get all loan payment
			loan_payment = models.LoanPayment.objects.filter(loan=loan)
			context_pay = []
			for item in loan_payment:
				temp_context= {}
				temp_context['form'] = forms.LoanPaymentForm(instance=item)
				temp_context['id'] = item.id
				context_pay.append(temp_context)

			context['loan_payment'] = context_pay
			context['loan'] = loan
			return render(request, 'bank/loan/form_cuotas.html', context)

		context['status'] = status
	loan = models.BankLoan.objects.all()
	form = forms.BankLoanForm()
	context['loan_bank'] = loan
	context['form'] = form
	return render(request, 'bank/loan/home.html', context)

def loan_edit_coutas(request, couta_id):
	couta = get_object_or_404(models.LoanPayment, id=couta_id)

	if request.method == 'POST':
		form = forms.LoanPaymentForm(request.POST, instance=couta)
		status_save_item = 'no'
		if form.is_valid():
			form.save()
			# Save and render
			status_save_item = 'yes'
			return render(request, 'bank/loan/status.html', {'status_save_item ': status_save_item })
		return render(request, 'bank/loan/status.html', {'status_save_item ': status_save_item })

	return render(request, 'bank/loan/status.html', {})

def loan_see(request, loan_id):
	loan = get_object_or_404(models.BankLoan, id=loan_id)
	loan_payment = models.LoanPayment.objects.filter(loan=loan)
	context = {}
	context["loan"] = loan
	context["loan_cuota"] = loan_payment
	return render(request, 'bank/loan/see.html', context)

def loan_pay(request, loan_id):
	loan = get_object_or_404(models.BankLoan, id=loan_id)

	context_pay = []
	context = {}
	status = ""

	if request.method == 'POST':
		form = forms.PartialPaymentForm(request.POST, loan=loan)
		status = "no"
		if form.is_valid():
			status = utils_bank.save_pay(form)

	# Create view to edit
	loan_payment = forms.PartialPaymentForm(loan=loan)

	context_items = utils_bank.get_all_pay(loan)
	context.update(context_items)

	context["loan"] = loan
	context["form"] = loan_payment
	context["status"] = status

	return render(request, 'bank/loan/pay.html', context)

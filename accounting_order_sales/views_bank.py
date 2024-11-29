from django.shortcuts import render, get_object_or_404

from . import models
from . import forms
from . import utils_bank

def loan_main(request):
	loan = models.BankLoan.objects.all()
	form = forms.BankLoanForm()
	context = {}
	context['loan_bank'] = loan
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
			i = 0;
			for item in loan_payment:
				context_pay.append(forms.LoanPaymentForm(instance=item))
				i = i+1
			print(context_pay)

			context['loan_payment'] = context_pay
			return render(request, 'bank/loan/form_cuotas.html', context)

		context['status'] = status
	loan = models.BankLoan.objects.all()
	form = forms.BankLoanForm()
	context['loan_bank'] = loan
	context['form'] = form
	return render(request, 'bank/loan/home.html', context)

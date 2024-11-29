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

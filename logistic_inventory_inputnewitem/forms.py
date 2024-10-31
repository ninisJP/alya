from django import forms


class SearchPurchaseItemForm(forms.Form):
	sap_code = forms.CharField(label="SAP", max_length=100, required=False)

class NewItemForm(forms.Form):
	quantity = forms.IntegerField(label="Cantidad")

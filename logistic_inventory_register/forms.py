from django import forms


class SearchGuideForm(forms.Form):
	date_start = forms.DateField(label="Fecha inicial (2024-01-01)", required=False)
	date_end = forms.DateField(label="Fecha final (2024-01-01)", required=False)

from django import forms


class SearchForm(forms.Form):
    name = forms.CharField(label="name", max_length=100)

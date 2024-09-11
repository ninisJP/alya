from django import forms

from .models import Brand

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ('name',)
        labels = {
            'name': 'Marca',
        }

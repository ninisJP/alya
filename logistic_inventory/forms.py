from django import forms

from .models import Brand, Type, Subtype, Item

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ('name',)
        labels = {
            'name': 'Marca',
        }

class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ('name', 'category')
        labels = {
            'name': 'Tipo',
            'category': 'Categoria',
        }

class SubtypeForm(forms.ModelForm):
    class Meta:
        model = Subtype
        fields = ('name', 'type')
        labels = {
            'name': 'Sub-tipo',
            'type': 'Tipo',
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('brand', 'description', 'item_id', 'quantity', 'subtype', 'unit')
        labels = {
            'brand': 'Marca',
            'description': 'Descripcion',
            'item_id': 'ID del item',
            'quantity': 'Cantidad',
            'unit': 'Unidad de medida',
        }

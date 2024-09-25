from django import forms
from dynamic_forms import DynamicField, DynamicFormMixin

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

class ItemForm(DynamicFormMixin, forms.ModelForm):

    type = forms.ModelChoiceField(
                queryset = Type.objects.all(),
            )

    def type_choice(form):
        ttype = form['type'].value()
        return Subtype.objects.filter(type=ttype)

    def type_initial(form):
        ttype = form['type'].value()
        return Subtype.objects.filter(type=ttype).first()

    subtype = DynamicField(
                forms.ModelChoiceField,
                queryset = type_choice,
            )

    class Meta:
        model = Item
        fields = ('brand', 'description', 'item_id', 'quantity', 'unit', 'subtype')
        labels = {
            'brand': 'Marca',
            'description': 'Descripcion',
            'item_id': 'ID del item',
            'quantity': 'Cantidad',
            'unit': 'Unidad de medida',
            'subtype': 'Sub-tipo',
        }

class SearchItemForm(forms.Form):
    type = forms.CharField(label="type", max_length=100, required=False)
    description = forms.CharField(label="description", max_length=100, required=False)
    item_id = forms.CharField(label="item_id", max_length=100, required=False)

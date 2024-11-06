from django import forms
from django.conf import settings
from django.urls import reverse_lazy

from dynamic_forms import DynamicField, DynamicFormMixin

import segno

from .models import Brand, Type, Subtype, Item

class Select2AjaxWidget(forms.Select):
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/select2@4.1.0/dist/css/select2.min.css',)
        }
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0/dist/js/select2.min.js',
        )

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['class'] = (attrs.get('class', '') + ' select2-ajax').strip()
        attrs['data-placeholder'] = 'Seleccione un codigo SAP'
        attrs['data-ajax--url'] = reverse_lazy('logistic_inventory_item_new_ajax')
        attrs['style'] = 'width: 100%;'
        return attrs

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

    def save(self, commit=True):
        instance = super(ItemForm, self).save(commit=False)
        if commit:
            instance.save()
            # Get id
            sap = str(instance.item.sap)
            # Create QR
            qrcode = segno.make_qr(sap)
            name = settings.MEDIA_ROOT + "item_qr/"+sap+".png"
            qrcode.save(name, scale=10)
            # Save QR
            instance.code_qr = name
            instance.save()

        return instance

    class Meta:
        model = Item
        fields = ('brand', 'description', 'item', 'quantity', 'unit', 'subtype')
        labels = {
            'brand': 'Marca',
            'description': 'Descripcion',
            'item': 'SAP',
            'quantity': 'Cantidad',
            'unit': 'Unidad de medida',
            'subtype': 'Sub-tipo',
        }
        widgets = {
            'item': Select2AjaxWidget(),
        }

class SearchItemForm(forms.Form):
    type = forms.CharField(label="type", max_length=100, required=False)
    description = forms.CharField(label="description", max_length=100, required=False)
    sap = forms.CharField(label="SAP", max_length=100, required=False)

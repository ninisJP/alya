from django import forms
from .models import Cronograma, Pago, PagoCronograma, Resolucion, ReciboSunat
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



class CronogramaForm(forms.ModelForm):
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    fecha_desembolso = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    # Agrega cualquier otro campo de fecha que necesites de manera similar

    class Meta:
        model = Cronograma
        fields = "__all__"  # O especifica los campos que necesitas

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Guardar"))

        # Aplica estilos a otros campos si es necesario
        for field_name, field in self.fields.items():
            if field_name not in [
                "fecha_inicio",
                "fecha_fin",
            ]:  # Evita sobrescribir la clase para los campos de fecha ya definidos
                field.widget.attrs["class"] = "form-control"


# forms htmx
class EditarMontoForm(forms.ModelForm):
    class Meta:
        model = PagoCronograma
        fields = ["monto_pago"]
        widgets = {
            "monto_pago": forms.NumberInput(attrs={"step": "0.01"}),
        }


class CambiarPDFPagoForm(forms.ModelForm):
    class Meta:
        model = PagoCronograma
        fields = ["pdf_pago"]


class EditarFechaPagoForm(forms.ModelForm):
    class Meta:
        model = PagoCronograma
        fields = ["fecha_pago"]
        widgets = {
            "fecha_pago": forms.DateInput(attrs={"type": "date"}),
        }


# METODO PDF
class PDFUploadForm(forms.Form):
    archivo_pdf = forms.FileField(label="Selecciona un archivo PDF")


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["pago_sunat"]

from django import forms
from django.core.exceptions import ValidationError
from .models import ReciboSunat
from decimal import Decimal
import datetime

class ReciboSunatForm(forms.ModelForm):
    class Meta:
        model = ReciboSunat
        fields = ['numero_recibo_sunat', 'monto_recibo_sunat', 'fecha_emision', 'tarjeta_pago', 'pdf_recibo_sunat']
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }




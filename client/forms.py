from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('legal_name', 'tax_id', 'phone', 'email', 'website', 'primary_contact')
        labels = {
            'legal_name': 'Empresa',
            'tax_id':'Ruc',
            'phone':'Telefono',
            'email':'Correo electronico',
            'website':'Pagina Web',
            'primary_contact':'Contacto'
        }
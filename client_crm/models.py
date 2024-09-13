from django.db import models
from client.models import Client


# Create your models here.
class Contract(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    terms = models.TextField()

    def __str__(self):
        return f"Contract {self.contract_number} - {self.client.legal_name}"

class Opportunity(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='opportunities')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2)
    probability = models.DecimalField(max_digits=5, decimal_places=2, help_text="Probabilidad de éxito (en %)")
    status = models.CharField(max_length=50, choices=(('open', 'Open'), ('won', 'Won'), ('lost', 'Lost')))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

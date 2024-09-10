from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Budget(models.Model):
    budget_name = models.CharField(max_length=100, default="", verbose_name="Presupuesto")
    budget_days = models.PositiveIntegerField()
    budget_price = models.DecimalField(max_digits=12, decimal_places=2, default=0) 
    budget_final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)   
    budget_number = models.CharField(max_length=10, blank=True)
    budget_date = models.DateField()
    budget_tax = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    budget_deliver = models.CharField(max_length=100, blank=True, null=True)
    budget_service = models.CharField(max_length=100, blank=True, null=True)
    budget_billing = models.CharField(max_length=100, blank=True, null=True)
    budget_warranty = models.CharField(max_length=100, blank=True, null=True)
    budget_expenses = models.DecimalField(max_digits=5, decimal_places=2)
    budget_utilty = models.DecimalField(max_digits=5, decimal_places=2) 

    def __str__(self):
        return f'{self.project.nombre} - {self.dias} días - {self.numero_cotizacion}'

class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    inventory = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField()
    measurement = models.CharField(max_length=50, blank=True, default='')
    unit_price = models.FloatField(default=0)
    daily_price = models.FloatField(default=0)
    final_price = models.FloatField(default=0)


  

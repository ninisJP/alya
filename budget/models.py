from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from decimal import Decimal

from project.models import Project

class Budget(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'Dólares'),
        ('PEN', 'Soles'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budgets', verbose_name="Proyecto")
    budget_name = models.CharField(max_length=100, default="", verbose_name="Presupuesto - Cotización")
    day = models.PositiveIntegerField()
    total_sol_partial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_dollar_partial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_sol_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_dollar_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    exchange = models.DecimalField(max_digits=10, decimal_places=3, default=3.75)
    quote_number = models.CharField(max_length=10, blank=True)
    date = models.DateField(default=timezone.now)
    money = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    delivery_time = models.CharField(max_length=100, blank=True, null=True)
    service_time = models.CharField(max_length=100, blank=True, null=True)
    billing = models.CharField(max_length=100, blank=True, null=True)
    warranty_time = models.CharField(max_length=100, blank=True, null=True)
    not_incluyed = models.TextField(blank=True, null=True)
    administration_expenses = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    administration_expenses_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    utility = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    utility_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.project.nombre} - {self.dias} días - {self.quote_number}'

    def calculate_total_value(self):
            # Sumar el precio de todos los items en soles (valor parcial)
        total_sol_partial = Decimal(0)
        for item in self.items.all():
            total_sol_partial += Decimal(item.precio_item_proyecto)

        self.total_sol_partial = total_sol_partial

        # Convertir el total parcial a dólares usando el tipo de cambio
        self.total_dollar_partial = total_sol_partial / Decimal(self.exchange)

        # Calcular gastos administrativos y utilidad
        self.administration_expenses_total = (total_sol_partial * Decimal(self.administration_expenses)) / Decimal(100)
        self.utility_total = (total_sol_partial * Decimal(self.utility)) / Decimal(100)

        # Sumar los gastos administrativos y la utilidad al total parcial para obtener el total final
        self.total_sol_final = total_sol_partial + self.administration_expenses_total + self.utility_total

        # Convertir el total final a dólares usando el tipo de cambio
        self.total_dollar_final = self.total_sol_final / Decimal(self.exchange)

    def save(self, *args, **kwargs):
        if not self.quote_number:
            last_budget = Budget.objects.all().order_by('id').last()
            if last_budget and last_budget.quote_number.startswith('COT'):
                try:
                    last_number = int(last_budget.quote_number.split('COT')[-1])
                    self.quote_number = f'COT{str(last_number + 1).zfill(3)}'
                except ValueError:
                    self.quote_number = 'COT001'
            else:
                self.quote_number = 'COT001'

        # Guardar la instancia primero para obtener la PK
        super().save(*args, **kwargs)

        # Luego calcular el valor total en soles y dólares sin volver a guardar el presupuesto
        self.calculate_total_value()


class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    inventory = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField()
    real_price = models.FloatField(default=0)
    real_price_day = models.FloatField(default=0)
    measure_unit = models.CharField(max_length=50, blank=True, default='')
    useful_life = models.PositiveIntegerField(default=365)
    price_item_project = models.FloatField(default=0)

    def __str__(self):
        return f'{self.inventory.descripcion} - {self.quantity} {self.measure_unit}'

    @property
    def price_total_day(self):
        return self.real_price_day * self.quantity

    def save(self, *args, **kwargs):
        # TODO : Asigna los valores del inventario relacionado
        #if not self.real_price:
        #    # ????
        #    self.real_price = self.inventory.ultimo_precio_compra

        # Calcular el precio diario en base a la vida útil proporcionada
        self.real_price_day = self.real_price / self.useful_life

        # Calcular el precio del ítem para todo el proyecto
        if self.useful_life == 1:
            self.price_item_project = self.real_price * self.quantity # Se cuenta la cantidad
        else:
            self.price_item_project = self.price_total_day * self.budget.day

        if not self.measure_unit:
            self.measure_unit = self.inventory.measure_unit

        super().save(*args, **kwargs)

        # Calcular y actualizar el presupuesto después de guardar el ítem
        self.budget.calculate_total_value()
        self.budget.save(update_fields=[
            'total_sol_partial', 'total_dollar_partial',
            'total_sol_final', 'total_dollar_final',
            'utility_total', 'administration_expenses_total'
        ])

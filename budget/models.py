from django.db import models
from client.models import Client

class Budget(models.Model):
    PERCENTAGE_CHOICES = [
        (5.00, '5%'),
        (8.00, '8%'),
        (10.00, '10%'),
    ]

    TIME_CHOICES = [
        ('2 days', '2 Días'),
        ('1 week', '1 Semana'),
        ('2 weeks', '2 Semanas'),
        ('1 month', '1 Mes'),
        ('2 months', '2 Meses'),
        ('6 months', '6 Meses'),
        ('1 year', '1 Año'),
        ('2 years', '2 Años'),
        ('3 years', '3 Años'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    budget_name = models.CharField(max_length=100, default="")
    budget_number = models.CharField(max_length=10, blank=True)
    budget_days = models.PositiveIntegerField()
    budget_date = models.DateField()
    budget_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_expenses = models.DecimalField(max_digits=5, decimal_places=2, choices=PERCENTAGE_CHOICES, default=5.00,)
    budget_utility = models.DecimalField(max_digits=5, decimal_places=2, choices=PERCENTAGE_CHOICES, default=5.00,)
    budget_final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_deliverytime = models.CharField(max_length=100, choices=TIME_CHOICES, blank=True, null=True,)
    budget_servicetime = models.CharField(max_length=100, choices=TIME_CHOICES, blank=True, null=True,)
    budget_warrantytime = models.CharField(max_length=100, choices=TIME_CHOICES, blank=True, null=True,)

    def calculate_budget_price(self):
        return sum(item.total_price for item in self.items.all())

    def calculate_final_price(self):
        price = self.budget_price
        expenses = price * (self.budget_expenses / 100)
        utility = price * (self.budget_utility / 100)
        return price + expenses + utility
        
    def save(self, *args, **kwargs):
        # Primero guarda el presupuesto sin calcular los valores, para asegurarse de que el ID esté disponible.
        if not self.pk:  # Si la instancia aún no tiene un primary key
            super().save(*args, **kwargs)  # Guardar para obtener un ID

        # Luego realiza los cálculos que dependen del ID
        self.budget_price = self.calculate_budget_price()
        self.budget_final_price = self.calculate_final_price()

        # Finalmente, guarda los cambios
        super().save(*args, **kwargs) 
        

    def __str__(self):
        return self.budget_name


class CatalogItem(models.Model):
    class Category(models.TextChoices):
        EQUIPO = 'Equipo'
        EPPS = 'EPPS'
        MATERIAL = 'Material'
        CONSUMIBLE = 'Consumible'
        HERRAMIENTA = 'Herramienta'

    category = models.CharField(max_length=100, choices=Category.choices, default=Category.EQUIPO)
    description = models.CharField(max_length=100)
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.name} <{self.description}> precio: {self.price} precio por dia: {self.price_per_day}'

class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(CatalogItem, on_delete=models.CASCADE, related_name='budget_items')
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.item.price * self.quantity
        super().save(*args, **kwargs)
        self.budget.save()

    def __str__(self):
        return f'{self.item} ----- {self.quantity} unidades'

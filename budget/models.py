from django.db import models
from client.models import Client
from decimal import Decimal

class Budget(models.Model):
    PERCENTAGE_CHOICES = [
        (0.00, '0%'),
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
    budget_expenses = models.DecimalField(max_digits=5, decimal_places=2, choices=PERCENTAGE_CHOICES, default=0.00,)
    budget_utility = models.DecimalField(max_digits=5, decimal_places=2, choices=PERCENTAGE_CHOICES, default=0.00,)
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
        total = price + expenses + utility
        return total

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

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"

class CatalogItem(models.Model):
    class Category(models.TextChoices):
        EQUIPO = 'Equipo'
        EPPS = 'EPPS'
        MATERIAL = 'Material'
        CONSUMIBLE = 'Consumible'
        HERRAMIENTA = 'Herramienta'
        MANODEOBRA = 'Mano de obra'

    category = models.CharField(max_length=100, choices=Category.choices, default=Category.EQUIPO)
    description = models.CharField(max_length=256, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sap = models.CharField(max_length=100, unique=True, db_index=True)
    unit = models.CharField(max_length=100, default='UND')

    def __str__(self):
        return f'{self.sap} <{self.description}> precio: {self.price}'
    
    class Meta:
        verbose_name = "Item Catálogo"
        verbose_name_plural = "Items de Catálogo"

class BudgetItem(models.Model):
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('CatalogItem', on_delete=models.CASCADE, related_name='budget_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    custom_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    custom_price_per_day = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    custom_price_per_hour = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    unit = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Si no se ha especificado una unidad, utilizar la unidad del catálogo
        if not self.unit:
            self.unit = self.item.unit

        # Si ya tenemos el precio total desde el Excel, lo usamos directamente
        if self.total_price:
            print(f"Usando el precio total proporcionado: {self.total_price}")
        else:
            # Asignar precios personalizados si no están definidos
            if self.custom_price is None:
                self.custom_price = self.item.price

            if self.custom_price_per_day is None:
                self.custom_price_per_day = self.item.price_per_day

            # Convertir a Decimal para cálculos precisos
            price = Decimal(self.custom_price)
            price_per_day = Decimal(self.custom_price_per_day)

            # Calcular total_price basado en la categoría
            if self.item.category in [
                CatalogItem.Category.HERRAMIENTA,
                CatalogItem.Category.MANODEOBRA,
                CatalogItem.Category.EPPS
            ]:
                self.total_price = price_per_day * Decimal(self.quantity) * Decimal(self.budget.budget_days)
            else:
                self.total_price = price * Decimal(self.quantity)

        # Ajustar la condición para la unidad 'HOR'
        if self.unit == 'HORAS':
            hours_per_day = 8  # Puedes ajustar este valor según tus necesidades
            total_hours = Decimal(self.budget.budget_days) * Decimal(hours_per_day) * Decimal(self.quantity)

            if total_hours > 0:
                self.custom_price_per_hour = self.total_price / total_hours
                self.custom_quantity = total_hours  # Total de horas trabajadas por todas las unidades
            else:
                self.custom_price_per_hour = Decimal('0.00')
                self.custom_quantity = Decimal('0.00')
        else:
            # Si la unidad no es 'HOR', asignamos None
            self.custom_price_per_hour = None
            self.custom_quantity = None

        super().save(*args, **kwargs)
        # Guardar el presupuesto para actualizar sus valores
        self.budget.save()

    class Meta:
        verbose_name = "Item Presupuesto"
        verbose_name_plural = "Items de Presupuesto"


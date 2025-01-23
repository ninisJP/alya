# See LICENSE file for copyright and license details.
"""
Models to budget
"""
from decimal import Decimal

from django.db import models


class Budget(models.Model):
    """
    Budget mode.

    Parameters
    ----------
    client : Client class Foreign Key
        client of budget
    """

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

    client = models.ForeignKey(
        'client.Client',
        on_delete=models.CASCADE,
        null=True
    )
    budget_name = models.CharField(max_length=100, default="")
    budget_number = models.CharField(max_length=10, blank=True)
    budget_days = models.PositiveIntegerField()
    budget_date = models.DateField()
    budget_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    budget_expenses = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        choices=PERCENTAGE_CHOICES,
        default=0.00
    )
    budget_utility = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        choices=PERCENTAGE_CHOICES,
        default=0.00
    )
    budget_final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    budget_deliverytime = models.CharField(
        max_length=100,
        choices=TIME_CHOICES,
        blank=True,
        null=True
     )
    budget_servicetime = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    budget_warrantytime = models.CharField(
        max_length=100,
        choices=TIME_CHOICES,
        blank=True,
        null=True
    )

    def calculate_budget_price(self):
        """
        Calculate the cost price from item price.
        """

        total = sum(item.total_price for item in self.items.all())
        return total

    def get_category_totals(self):
        """
        Calculate the price by categoy.
        """

        category_totals = {}
        for budget_item in self.items.all():
            category = budget_item.item.category

            # Check if category exist
            if category not in category_totals:
                category_totals[category] = Decimal(0.00)

            category_totals[category] += budget_item.total_price
        return category_totals

    def update_budget_price(self):
        """
        Update the budget cost price.
        """

        self.budget_price = self.calculate_budget_price()
        self.save(update_fields=['budget_price'])

    def save(self, *args, **kwargs):
        """
        Custom save.

        Calculate the budget cost price if any item is changed.
        """

        if not self.pk:
            super().save(*args, **kwargs)

        if not (self.budget_price and ('update_budget_price' not in kwargs)):
            self.budget_price = self.calculate_budget_price()

        super().save(*args, **kwargs)

    def __str__(self):
        """
        Message to show when use the class in print
        """

        return self.budget_name

    class Meta:
        """
        Add versobe name in singular an plural
        """

        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"


class CatalogItem(models.Model):
    """
    Class to item from catalog.
    """

    class Category(models.TextChoices):
        """
        Types of category.
        """

        EQUIPO = 'Equipo'
        EPPS = 'EPPS'
        MATERIAL = 'Material'
        CONSUMIBLE = 'Consumible'
        HERRAMIENTA = 'Herramienta'
        MANODEOBRA = 'Mano de obra'

    category = models.CharField(
        max_length=100,
        choices=Category.choices,
        default=Category.EQUIPO
    )
    description = models.CharField(max_length=256, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    life_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    sap = models.CharField(max_length=100, unique=True, db_index=True)
    unit = models.CharField(max_length=100, default='UND')

    def __str__(self):
        """
        Message to show when use the class in print
        """
        return f'{self.sap} <{self.description}> precio: {self.price}'

    class Meta:
        """
        Add versobe name in singular an plural
        """

        verbose_name = "Item Catálogo"
        verbose_name_plural = "Items de Catálogo"


class BudgetItem(models.Model):
    """
    Class to item from budget.
    """

    COIN = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    budget = models.ForeignKey(
        'Budget',
        on_delete=models.CASCADE,
        related_name='items'
    )
    item = models.ForeignKey(
        'CatalogItem',
        on_delete=models.CASCADE,
        related_name='budget_items'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00
    )
    custom_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    custom_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    custom_price_per_day = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    custom_price_per_hour = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        blank=True
    )
    unit = models.CharField(max_length=100, blank=True, null=True)
    coin = models.CharField(
        max_length=3,
        choices=COIN,
        default='PEN',
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        """
        Custom save.

        Calculate the budget cost price if any item is changed.
        """

        # Use the catalog item unit by default
        if not self.unit:
            self.unit = self.item.unit

        # TODO: Check: recalculate all time the total price
        # Use the excel total price if exist
        if not self.total_price:
            if self.custom_price is None:
                self.custom_price = self.item.price
            if self.custom_price_per_day is None:
                self.custom_price_per_day = self.item.price_per_day

            # Convert to float for precition
            price = Decimal(self.custom_price)
            price_per_day = Decimal(self.custom_price_per_day)

            # Price by category
            if self.item.category in [
                CatalogItem.Category.HERRAMIENTA,
                CatalogItem.Category.MANODEOBRA,
                CatalogItem.Category.EPPS
            ]:
                self.total_price = (
                    price_per_day *
                    Decimal(self.quantity) *
                    Decimal(self.budget.budget_days)
                )
            else:
                self.total_price = price * Decimal(self.quantity)

        if "HORAS" in (self.unit or ""):
            hours_per_day = 8
            # Get unit (e.g., 'PAQ', 'UND', 'PAR')
            # parts = self.unit.split("/")
            # secondary_unit = parts[1] if len(parts) > 1 else "UND"
            total_hours = (
                Decimal(self.budget.budget_days) *
                Decimal(hours_per_day) *
                Decimal(self.quantity)
            )

            if 0 < total_hours:
                self.custom_price_per_hour = self.total_price / total_hours
                self.custom_quantity = total_hours
            else:
                self.custom_price_per_hour = Decimal('0.00')
                self.custom_quantity = Decimal('0.00')
        else:
            self.custom_price_per_hour = None
            self.custom_quantity = None

        super().save(*args, **kwargs)
        self.budget.save()

    class Meta:
        """
        Add versobe name in singular an plural
        """

        verbose_name = "Item Presupuesto"
        verbose_name_plural = "Items de Presupuesto"

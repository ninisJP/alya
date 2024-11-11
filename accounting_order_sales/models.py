from django.db import models
from django.core.validators import FileExtensionValidator
from logistic_suppliers.models import Suppliers
from project.models import Project
from client.models import Client
from decimal import Decimal
from django.db.models.functions import TruncMonth
from django.core.exceptions import ValidationError
from django.db.models import Sum,DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal, ROUND_HALF_UP
from django.utils.module_loading import import_string


class SalesOrder(models.Model):
    sapcode = models.PositiveBigIntegerField(default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    detail = models.CharField(max_length=255)
    date = models.DateField()
    total_sales_order = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)


    def update_total_sales_order(self):
        self.total_sales_order = sum(item.price_total for item in self.items.all())
        self.save()

    def total_hours_man(self):
        # Cargamos `Task` de forma diferida usando `import_string`
        Task = import_string("follow_control_card.models.Task")
        return Task.objects.filter(sale_order=self).aggregate(total_hours=Sum('task_time'))['total_hours'] or 0.00

    def get_total_price_sum(self):
        return self.items.aggregate(total_price_sum=Sum('price_total'))['total_price_sum'] or 0.00

    def get_utility(self):
        total_purchase_orders = sum(purchase_order.total_purchase_order for purchase_order in self.purchase_orders.all())
        utility = Decimal(self.total_sales_order) - Decimal(total_purchase_orders or 0)
        # Redondea a 2 decimales
        return utility.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.sapcode} - {self.project if self.project else 'Sin Proyecto'} - {self.detail}"
    class Meta:
        verbose_name = "Orden Venta"
        verbose_name_plural = "Ordenes de Venta"

class SalesOrderItem(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    sap_code = models.CharField(max_length=255, default="")
    description = models.CharField(max_length=255, default="")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal(0))
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_of_measurement = models.CharField(max_length=255, default="UND")
    remaining_requirement = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.amount} unidades"

    def update_remaining_requirement(self):
        """
        Calcula el remaining_requirement basado en las cantidades solicitadas en las RequirementOrderItems asociadas.
        """
        cantidad_solicitada = sum(item.quantity_requested for item in self.requirementorderitem_set.all())
        self.remaining_requirement = max(self.amount - cantidad_solicitada, 0)
        self.save()

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para inicializar remaining_requirement al valor de amount cuando se crea el objeto.
        """

        if self.pk is None:  # Si el objeto aún no ha sido guardado (nuevo objeto)
            self.remaining_requirement = self.amount

        super().save(*args, **kwargs)  # Llamar al método save original

        # Actualizar la orden de venta (SalesOrder) total después de guardar
        self.salesorder.update_total_sales_order()

    class Meta:
        verbose_name = "Item Orden Venta"
        verbose_name_plural = "Items Orden Venta"

class PurchaseOrder(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE,related_name="purchase_orders")
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    requested_date = models.DateField(blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)  # Fecha programada
    requested_by = models.CharField(max_length=20, verbose_name="Encargado", blank=True, null=True)
    acepted = models.BooleanField(default=True)

    # @property
    # def total_purchase_order(self):
    #     # Suma el campo `price_total` de todos los PurchaseOrderItem asociados a esta orden
    #     return self.items.aggregate(total=Sum('price_total'))['total'] or 0

    @property
    def total_purchase_order(self):
        return self.items.aggregate(
            total=Coalesce(Sum('price_total'), Decimal(0), output_field=DecimalField())
        )['total']

    def __str__(self):
        return f"Orden de Compra {self.id} para la Orden de Venta {self.salesorder.sapcode} - Solicitada el {self.requested_date}"

    class Meta:
        verbose_name = "Orden Compra"
        verbose_name_plural = "Ordenes de Compra"

class PurchaseOrderItem(models.Model):
    CLASS_PAY_CHOICES = [
        ('bancos', 'Bancos'),
        ('planillas', 'Planillas'),
        ('servicios', 'Servicios'),
        ('sunat', 'SUNAT'),
        ('proveedores', 'Proveedores'),
    ]

    TYPE_PAY_CHOICES = [
        ('prestamo', 'Préstamo'),
        ('tarjeta', 'Tarjeta'),
        ('sueldo', 'Sueldo'),
        ('bonos', 'Bonos'),
        ('afp', 'AFP'),
        ('graticaciones', 'Gratificaciones'),
        ('liquidacion', 'Liquidación'),
        ('vacaciones', 'Vacaciones'),
        ('cts', 'CTS'),
        ('recibo_honorarios', 'Recibo por Honorarios'),
        ('proveedores', 'Proveedores'),
        ('fraccionamiento', 'Fraccionamiento'),
        ('planilla', 'Planilla'),
        ('pdt', 'PDT'),
    ]

    purchaseorder = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    sales_order_item = models.ForeignKey(SalesOrderItem, on_delete=models.CASCADE)
    sap_code = models.CharField(max_length=255, default="")
    class_pay = models.CharField(max_length=50, choices=CLASS_PAY_CHOICES, default='proveedores')  # Elegir entre clases
    type_pay = models.CharField(max_length=50, choices=TYPE_PAY_CHOICES, default='proveedores')  # Elegir entre tipos
    quantity_requested = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(1))
    notes = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, blank=True, null=True)
    mov_number = models.CharField(max_length=255, null=True, blank=True, default='')
    bank = models.CharField(max_length=100, null=True, blank=True)
    total_renditions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total Renditions")

    bank_statement = models.ForeignKey(
        'BankStatements',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conciliated_items',
        verbose_name="Extracto Bancario Conciliado"
    )

    def save(self, *args, **kwargs):
        if self.price is not None and self.quantity_requested is not None:
            self.price_total = self.price * self.quantity_requested
        else:
            self.price_total = None
        super(PurchaseOrderItem, self).save(*args, **kwargs)


    def __str__(self):
        return f"Item {self.sap_code} - {self.quantity_requested} units - Total {self.price_total}"

    def update_total_renditions(self):
        # Recalcula la suma de todas las rendiciones y la guarda en el campo correspondiente
        total = self.renditions.aggregate(total=Sum('amount'))['total'] or 0
        self.total_renditions = total
        self.save()

    class Meta:
        verbose_name = "Item Orden Compra"
        verbose_name_plural = "Items Orden Compra"

class Rendition(models.Model):
    purchase_order_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name="renditions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Rendition Amount")
    photo = models.ImageField(upload_to='renditions/', blank=True, null=True, verbose_name="Invoice/Receipt Photo")
    date = models.DateField(verbose_name="Rendition Date", blank=True, null=True)
    accepted = models.BooleanField(default=False, verbose_name="Accepted")

    # Campos series y correlativo en inglés
    series = models.CharField(max_length=50, null=True, blank=True, verbose_name="Series")
    correlative = models.CharField(max_length=50, null=True, blank=True, verbose_name="Correlative Number")

    # Método para evitar registros duplicados
    def clean(self):
        # Solo verificar si series y correlative tienen valores
        if self.series and self.correlative:
            # Verificar si ya existe una rendición con el mismo series y correlative para el mismo ítem
            if Rendition.objects.filter(series=self.series, correlative=self.correlative).exclude(pk=self.pk).exists():
                raise ValidationError('Ya existe una factura o boleta registrada con esta serie y correlativo.')

    def update_total_renditions(self):
        # Recalcula la suma de todas las rendiciones y la guarda en el campo correspondiente
        total = self.purchase_order_item.renditions.aggregate(total=Sum('amount'))['total'] or 0
        self.purchase_order_item.total_renditions = total
        self.purchase_order_item.save()

    def save(self, *args, **kwargs):
        # Verifica antes de guardar si hay duplicados
        self.clean()
        # Guardar la rendición
        super(Rendition, self).save(*args, **kwargs)
        # Actualizar el total de rendiciones en el PurchaseOrderItem relacionado
        self.update_total_renditions()

    def __str__(self):
        return f"Rendiciones para {self.amount} - {self.purchase_order_item.sap_code} el {self.date}"

    class Meta:
        verbose_name = "Rendición"
        verbose_name_plural = "Rendiciones"

class Bank(models.Model):
    bank_name = models.CharField(max_length=70, verbose_name='Banco')
    bank_account = models.CharField(max_length=30, verbose_name='Número de cuenta bancaria')
    bank_detail = models.CharField(max_length=200,verbose_name='Detalles')
    bank_current_mount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Monto Total');

    def __str__(self):
        return f'Banco: {self.bank_name} - Cuenta: {self.bank_account}'

    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"

class BankStatements(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Banco')
    operation_date = models.DateField(verbose_name='Fecha de Operación', null=True, blank=True)
    reference = models.CharField(max_length=100, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    itf = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='ITF', null=True, blank=True)
    number_moviment = models.CharField(max_length=50, verbose_name='Número de Movimiento', default='')

    def __str__(self):
        return f'Movimiento: {self.number_moviment} - Referencia: {self.reference}'

    class Meta:
        verbose_name = "Extracto de Bancos"
        verbose_name_plural = "Extractos Bancarios"

class BankStatementManager(models.Manager):
    def by_month(self, year, month):
        return self.annotate(
            month=TruncMonth('operation_date')
        ).filter(
            operation_date__year=year,
            operation_date__month=month,
        )

class CollectionOrders(models.Model):
    TIPO_COBRO_CHOICES = [
        ('factoring', 'Factoring'),
        ('directo', 'Directo'),
    ]
    orden_venta = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, verbose_name="Orden de Venta")
    serie_correlativo = models.CharField(max_length=100, verbose_name="Serie y Correlativo", null=True, blank=True)
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión", null=True, blank=True)
    cliente = models.CharField(max_length=255, verbose_name="Cliente", null=True, blank=True)
    ruc_cliente = models.CharField(max_length=11, verbose_name="RUC Cliente", null=True, blank=True)
    tipo_moneda = models.CharField(max_length=20, verbose_name="Tipo de Moneda", null=True, blank=True)
    descripcion = models.TextField(verbose_name="Descripción", null=True, blank=True)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe Total", null=True, blank=True)
    detraccion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Detracción", null=True, blank=True)
    monto_neto_cobrar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Neto a Cobrar", null=True, blank=True)
    total_cuotas = models.IntegerField(verbose_name="Total de Cuotas", null=True, blank=True)
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento", null=True, blank=True)
    tipo_cobro = models.CharField(max_length=20, choices=TIPO_COBRO_CHOICES, verbose_name="Tipo de Cobro", null=True, blank=True)
    desc_factoring = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Descuento Factoring (%)", null=True, blank=True)
    extracto_banco = models.ForeignKey(BankStatements, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Extracto Bancario")
    factura_pagado = models.BooleanField(default=False, verbose_name="Factura Pagada")

    def save(self, *args, **kwargs):
        if self.desc_factoring and self.monto_neto_cobrar:
            descuento = (self.desc_factoring / 100) * self.monto_neto_cobrar
            self.monto_neto_cobrar -= descuento

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.serie_correlativo} - {self.cliente}"

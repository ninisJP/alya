from django.db import models
from django.core.validators import FileExtensionValidator
from logistic_suppliers.models import Suppliers
from project.models import Project
from client.models import Client
from decimal import Decimal
from django.db.models.functions import TruncMonth


class SalesOrder(models.Model):
    sapcode = models.PositiveBigIntegerField(default=0) 
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)  
    detail = models.CharField(max_length=255)
    date = models.DateField()

    def update_total_sales_order(self):
        self.total_sales_order = sum(item.price_total for item in self.items.all())
        self.save()

    def __str__(self):
        return f"{self.sapcode} - {self.project if self.project else 'Sin Proyecto'} - {self.detail}"


class SalesOrderItem(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    sap_code = models.CharField(max_length=255, default="") 
    description = models.CharField(max_length=255, default="")
    amount = models.IntegerField(null=True, default=0)
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
        # Solo inicializar el remaining_requirement cuando el objeto se crea por primera vez
        if self.pk is None:  # Si el objeto aún no ha sido guardado (nuevo objeto)
            self.remaining_requirement = self.amount

        super().save(*args, **kwargs)  # Llamar al método save original

        # Actualizar la orden de venta (SalesOrder) total después de guardar
        self.salesorder.update_total_sales_order()

class PurchaseOrder(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE,related_name="purchase_orders")
    description = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True)
    requested_date = models.DateField(blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)
    requested_by = models.CharField(max_length=20, verbose_name="Encargado", blank=True, null=True)
    acepted = models.BooleanField(default=True)

    def __str__(self):
        return f"Orden de Compra {self.id} para la Orden de Venta {self.salesorder.sapcode} - Solicitada el {self.requested_date}"

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
    quantity_requested = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, blank=True, null=True)
    mov_number = models.CharField(max_length=255, null=True, blank=True, default='')
    bank = models.CharField(max_length=100, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.price is not None and self.quantity_requested is not None:
            self.price_total = self.price * self.quantity_requested
        else:
            self.price_total = None
        super(PurchaseOrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.sap_code} - {self.quantity_requested} units - Total {self.price_total}"

class Rendition(models.Model):
    purchase_order_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name="renditions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Rendido")
    photo = models.ImageField(upload_to='renditions/', blank=True, null=True, verbose_name="Foto de la Factura/Recibo")
    date = models.DateField(auto_now_add=True, verbose_name="Fecha de Rendición")

    def __str__(self):
        return f"Rendición por {self.amount} - {self.purchase_order_item.sap_code} el {self.date}"



    
    
class Bank(models.Model):
    bank_name = models.CharField(max_length=70, verbose_name='Banco')
    bank_account = models.CharField(max_length=30, verbose_name='Número de cuenta bancaria')
    bank_detail = models.CharField(max_length=200,verbose_name='Detalles')
    bank_current_mount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Monto Total');
    
    def __str__(self):
        return f'Banco: {self.bank_name} - Cuenta:{self.bank_account}'
    
    
class BankStatements(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Banco')
    operation_date = models.DateField(verbose_name='Fecha de Operación', null=True, blank=True)
    reference = models.CharField(max_length=100, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    itf = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='ITF', null=True, blank=True)
    number_moviment = models.CharField(max_length=50, verbose_name='Número de Movimiento', default='')

    def __str__(self):
        return f'Movimiento: {self.number_moviment} - Referencia: {self.reference}'   
    
class BankStatementManager(models.Manager):
    def by_month(self, year, month):
        return self.annotate(
            month=TruncMonth('operation_date') 
        ).filter(
            operation_date__year=year,
            operation_date__month=month,
        )

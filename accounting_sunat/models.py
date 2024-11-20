from django.db import models

# Create your models here.

from django.db import models

# Create your models here.from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal


class Cronograma(models.Model):
    fecha_inicio = models.DateField()
    fecha_desembolso = models.DateField()
    entidad = models.CharField(max_length=100)
    moneda = models.CharField(max_length=50)
    numero_cuotas = models.PositiveIntegerField()
    monto_cuota = models.DecimalField(max_digits=15, decimal_places=2)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2)
    detalle = models.CharField(
        max_length=255
    )  # Ajusta la longitud máxima según sea necesario
    doc = models.FileField(upload_to="pdf/", null=True, blank=True, default=None)

    def __str__(self):
        return f"Cronograma {self.id} - {self.entidad} - {self.detalle}"


class PagoCronograma(models.Model):
    cronograma = models.ForeignKey(Cronograma, on_delete=models.CASCADE)
    fecha_pago = models.DateField()
    monto_para_pagar = models.DecimalField(max_digits=15, decimal_places=2)  # Monto que se espera pagar según el cronograma
    monto_pago = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Monto efectivamente pagado
    pdf_pago = models.FileField(upload_to="pagos_pdfs/", null=True, blank=True, default=None)

    def __str__(self):
        return f"Pago programado: {self.monto_para_pagar} - Pago realizado: {self.monto_pago} el {self.fecha_pago} - Detalle: {self.cronograma.detalle}"



@receiver(post_save, sender=Cronograma)
def crear_pagos(sender, instance, created, **kwargs):
    if created:
        fecha_actual = instance.fecha_inicio
        for i in range(instance.numero_cuotas):
            # Ajuste especial para el cuarto pago
            if i == 3:
                fecha_actual += relativedelta(months=2)
            # Ajuste especial para el sexto pago
            elif i == 5:
                fecha_actual += relativedelta(months=5)
            else:
                fecha_actual += relativedelta(months=1)

            PagoCronograma.objects.create(
                cronograma=instance,
                fecha_pago=fecha_actual,
                monto_para_pagar=instance.monto_cuota,
            )
class Resolucion(models.Model):
    numero_resolucion = models.CharField(max_length=255)
    tipo_resolucion = models.CharField(max_length=255)
    tiempo_aplazamiento = models.CharField(max_length=255)
    archivo_pdf = models.FileField(upload_to='pdfs/')
    descripcion = models.TextField()  # Campo añadido para la descripción
    monto_tributo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return self.numero_resolucion

# ! este otro no si puedes eliminalo.
class DetallePago(models.Model):
    resolucion = models.ForeignKey(
        Resolucion, on_delete=models.CASCADE, related_name="detalles_pago"
    )
    id_pago = models.CharField(max_length=10)
    vencimiento = models.DateField()
    amortizacion = models.DecimalField(max_digits=10, decimal_places=2)
    interes = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)


# * este sirve :) 
from django.db import models
from decimal import Decimal

class Pago(models.Model):
    resolucion = models.ForeignKey('Resolucion', related_name='pagos', on_delete=models.CASCADE)
    numero_cuota = models.CharField(max_length=255)
    vencimiento = models.DateField()
    amortizacion = models.DecimalField(max_digits=10, decimal_places=2)
    interes = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    pago_sunat = models.FileField(upload_to='pagos_sunat/', null=True, blank=True)
    monto_pagado_sunat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.resolucion} - Cuota {self.numero_cuota}"

    def update_monto_pagado_sunat(self):
        total_recibos = self.recibos_sunat.all().aggregate(models.Sum('monto_recibo_sunat'))['monto_recibo_sunat__sum']
        if total_recibos is None:
            total_recibos = 0
        self.monto_pagado_sunat = Decimal(total_recibos).quantize(Decimal('0.00'))
        self.save()

    def save(self, *args, **kwargs):
        # Asegúrate de que 'monto_pagado_sunat' sea un Decimal
        if not isinstance(self.monto_pagado_sunat, Decimal):
            self.monto_pagado_sunat = Decimal(str(self.monto_pagado_sunat))

        # Redondear ambos valores a dos decimales antes de la comparación
        total_rounded = self.total.quantize(Decimal('0.00'))
        monto_pagado_rounded = self.monto_pagado_sunat.quantize(Decimal('0.00'))

        self.pagado = total_rounded == monto_pagado_rounded
        super(Pago, self).save(*args, **kwargs)

class ReciboSunat(models.Model):
    pago = models.ForeignKey(Pago, related_name='recibos_sunat', on_delete=models.CASCADE)
    numero_recibo_sunat = models.CharField(max_length=255, verbose_name='Número de Recibo')
    monto_recibo_sunat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    fecha_emision = models.DateField(verbose_name='Fecha de Emisión')
    tarjeta_pago = models.CharField(max_length=255, verbose_name='Tarjeta de Pago')
    pdf_recibo_sunat = models.FileField(upload_to='recibos_sunat/', null=True, blank=True, verbose_name='PDF')
    
    def __str__(self):
        return f"Recibo Sunat #{self.numero_recibo_sunat} - Pago {self.pago.id}"

    def save(self, *args, **kwargs):
        super(ReciboSunat, self).save(*args, **kwargs)
        self.pago.update_monto_pagado_sunat()

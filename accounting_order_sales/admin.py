from django.contrib import admin
from .models import *

# Registro del modelo SalesOrder sin el inline de SalesOrderItem
@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('sapcode', 'project', 'detail', 'date', 'days')  # Añadir el campo 'days' en la lista de visualización

# Registro del modelo SalesOrderItem (opcional, solo si quieres gestionarlo también por separado)
@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = ('salesorder', 'sap_code', 'description', 'amount', 'price', 'price_total')

# Otros registros de modelos
admin.site.register(Bank)
admin.site.register(BankStatements)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(Rendition)

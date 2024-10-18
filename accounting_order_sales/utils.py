import re
from decimal import Decimal
from openpyxl import load_workbook
from django.shortcuts import get_object_or_404
from .models import SalesOrder, SalesOrderItem

def limpiar_valor(valor):
    if isinstance(valor, str):
        valor = re.sub(r'[^\d.,]', '', valor)
        try:
            return Decimal(valor.replace(',', ''))
        except ValueError:
            return None
    return valor

def procesar_archivo_excel(archivo_excel, salesorder_id):
    workbook = load_workbook(archivo_excel)
    sheet = workbook.active

    # Verificar que la orden de venta existe
    salesorder = get_object_or_404(SalesOrder, pk=salesorder_id)

    # Nombres de las columnas
    col_nro_articulo = 'Número de artículo'
    col_desc_articulo = 'Descripción del artículo'
    col_cantidad = 'Cantidad'
    col_precio_bruto = 'Precio bruto'
    col_total_bruto = 'Total bruto (ML)'
    col_unidad_medida = 'Unidad de medida'  # Nueva columna para la unidad de medida

    # Encuentra los índices de las columnas
    header = [cell.value for cell in sheet[1]]
    idx_nro_articulo = header.index(col_nro_articulo)
    idx_desc_articulo = header.index(col_desc_articulo)
    idx_cantidad = header.index(col_cantidad)
    idx_precio_bruto = header.index(col_precio_bruto)
    idx_total_bruto = header.index(col_total_bruto)
    idx_unidad_medida = header.index(col_unidad_medida)  # Índice de la unidad de medida

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[idx_nro_articulo] is None or row[idx_desc_articulo] is None or row[idx_cantidad] is None:
            continue

        cantidad = limpiar_valor(row[idx_cantidad])
        precio_bruto = limpiar_valor(row[idx_precio_bruto])
        total_bruto = limpiar_valor(row[idx_total_bruto])
        unidad_medida = row[idx_unidad_medida]  # Obtener unidad de medida directamente

        if cantidad is None:
            continue  # Si no se puede convertir la cantidad, saltar esta fila

        SalesOrderItem.objects.create(
            salesorder=salesorder,
            sap_code=row[idx_nro_articulo],
            description=row[idx_desc_articulo],
            amount=cantidad,
            price=precio_bruto,
            price_total=total_bruto,
            unit_of_measurement=unidad_medida  # Guardar la unidad de medida
        )


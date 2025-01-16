import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Budget, BudgetItem
from django.conf import settings
import pandas as pd
import decimal
from decimal import Decimal
from .models import CatalogItem
from django.db import transaction

def export_budget_report_to_excel(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    # Cargar la plantilla de Excel
    file_path = f'{settings.BASE_DIR}/static/plantilla.xlsx'
    plantilla = openpyxl.load_workbook(file_path)

    # Agrupar los ítems por categoría (content_type)
    items_by_category = {}
    for item in budget.items.all():
        categoria = item.item.category
        if categoria not in items_by_category:
            items_by_category[categoria] = []
        items_by_category[categoria].append(item)

    # Crear una hoja para cada categoría de ítem
    for categoria, items in items_by_category.items():
        ws_categoria = plantilla.create_sheet(title=f"{categoria}")
        _crear_hoja_presupuesto(ws_categoria, budget, {categoria: items}, simbolo='S/')

    # Crear una hoja final con el resumen de todos los ítems y valores finales
    ws_resumen = plantilla.create_sheet(title="Resumen Final")
    _crear_hoja_resumen(ws_resumen, budget, items_by_category)

    # Crear la hoja de cotización
    _create_quote(plantilla, budget)
    
    # Plantilla presupuesto
    _create_budget(plantilla, budget, items_by_category)
    
    # Crear la respuesta HTTP con el nombre del archivo según el nombre del presupuesto
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{budget.budget_name}.xlsx"'
    plantilla.save(response)

    return response

def _crear_hoja_presupuesto(ws, budget, items_by_category, simbolo='S/'):
    # Estilos generales
    print("Items by Category:", items_by_category)
    header_font = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
    cell_font = Font(name="Calibri", size=11)
    alignment_center = Alignment(horizontal="center", vertical="center")
    fill_blue = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Título del presupuesto
    ws['A1'] = f'PRESUPUESTO: {budget.budget_name} ({simbolo})'
    ws['A1'].font = Font(bold=True, size=16, name="Calibri")
    ws['A1'].alignment = alignment_center

    # Encabezados de la tabla
    headers = ['ITEM', 'DESCRIPCION DE ITEM', 'CATEGORÍA', 'CANTIDAD', 'MONEDA','PRECIO UNITARIO', 'SUBTOTAL']
    ws.append(headers)
    for cell in ws[2]:  # Segunda fila
        cell.font = header_font
        cell.fill = fill_blue
        cell.alignment = alignment_center
        cell.border = thin_border

    # Datos de los ítems
    for items in items_by_category.values():
        for item in items:
            subtotal = item.total_price
            row = [
                item.item.sap,
                item.item.description,
                item.item.category,
                item.quantity,
                item.coin,
                item.item.price,
                subtotal
            ]
            print(f"Adding row: {row}")
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.font = cell_font
                cell.alignment = alignment_center
                cell.border = thin_border

    # Añadir el resumen financiero al final
    ws.append([''])
    resumen = []

    # Verificar si budget.budget_expenses no es cero para evitar la división por cero
    if budget.budget_expenses != 0:
        percent = int(budget.budget_expenses) / 100
        print(f' heli {percent}')
        utilidad = budget.budget_price * Decimal(percent)
        total_final = budget.budget_price - utilidad
    else:
        utilidad = 0
        total_final = budget.budget_price  # En caso de que sea cero, no se calcula la utilidad y el total final es igual al precio

    # Ahora creamos el resumen con los valores calculados
    resumen = [
        ('TOTAL PARCIAL', f'S/ {budget.budget_price:.2f}'),
        ('GASTOS ADMINISTRATIVOS', f'%{budget.budget_expenses}'),
        ('UTILIDAD', f'S/ {utilidad:.2f}'),
        ('TOTAL FINAL', f'S/ {total_final:.2f}')
    ]
    
    for label, value in resumen:
        ws.append([label, '', '', '', '', value])
        for cell in ws[ws.max_row]:
            cell.font = cell_font if label != 'TOTAL FINAL' else Font(bold=True, size=12, color="FF0000")
            cell.alignment = alignment_center
            cell.border = thin_border
            if label == 'TOTAL FINAL':
                cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    # Ajustar ancho de las columnas
    for column in ws.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value)  # Evitar valores vacíos
        adjusted_width = max_length + 2
        ws.column_dimensions[column[0].column_letter].width = adjusted_width

from openpyxl.cell.cell import MergedCell 

def _crear_hoja_resumen(ws, budget, items_by_category):
    # Estilos generales
    header_font = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
    cell_font = Font(name="Calibri", size=11)
    alignment_center = Alignment(horizontal="center", vertical="center")
    fill_blue = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Título del resumen
    ws['A1'] = f'RESUMEN FINAL DEL PRESUPUESTO: {budget.budget_name}'
    ws['A1'].font = Font(bold=True, size=16, name="Calibri")
    ws['A1'].alignment = alignment_center

    # Encabezados de la tabla
    headers = ['ITEM', 'DESCRIPCIÓN', 'CATEGORÍA', 'CANTIDAD','MONEDA', 'PRECIO UNITARIO', 'SUBTOTAL']
    ws.append(headers)
    for cell in ws[2]:
        cell.font = header_font
        cell.fill = fill_blue
        cell.alignment = alignment_center
        cell.border = thin_border

    # Listado de todos los ítems agrupados por categoría
    for categoria, items in items_by_category.items():
        ws.append([categoria])  # Título de categoría
        for item in items:
            subtotal = item.total_price
            row = [
                item.item.sap,
                item.item.description,
                item.item.category,
                item.quantity,
                item.coin,
                item.item.price,
                subtotal,
            ]
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.font = cell_font
                cell.alignment = alignment_center
                cell.border = thin_border

    # Añadir el resumen financiero al final
    ws.append([''])
    resumen = []

    # Verificar si budget.budget_expenses no es cero para evitar la división por cero
    if budget.budget_expenses != 0:
        percent = int(budget.budget_expenses) / 100
        print(f' heli {percent}')
        utilidad = budget.budget_price * Decimal(percent)
        total_final = budget.budget_price - utilidad
    else:
        utilidad = 0
        total_final = budget.budget_price  # En caso de que sea cero, no se calcula la utilidad y el total final es igual al precio

    # Ahora creamos el resumen con los valores calculados
    resumen = [
        ('TOTAL PARCIAL', f'S/ {budget.budget_price:.2f}'),
        ('GASTOS ADMINISTRATIVOS', f'%{budget.budget_expenses}'),
        ('UTILIDAD', f'S/ {utilidad:.2f}'),
        ('TOTAL FINAL', f'S/ {total_final:.2f}')
    ]

    for label, value in resumen:
        ws.append([label, '', '', '', '', value])
        for cell in ws[ws.max_row]:
            cell.font = cell_font if label != 'TOTAL FINAL' else Font(bold=True, size=12, color="FF0000")
            cell.alignment = alignment_center
            cell.border = thin_border
            if label == 'TOTAL FINAL':
                cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    # Ajustar ancho de las columnas
    for column in ws.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value)  # Evitar valores vacíos
        adjusted_width = max_length + 2
        ws.column_dimensions[column[0].column_letter].width = adjusted_width
        
        
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

def _create_budget(plantilla, budget, items_by_category):
    # Accedemos a la hoja "PRESUPUESTO"
    sheet = plantilla['PRESUPUESTO']

    # Título del presupuesto
    title_cell = sheet['B1']
    title_cell.value = f'PRESUPUESTO: {budget.budget_name}'
    title_cell.font = Font(name="Calibri", size=6, bold=True)  # Aplicar formato a la celda B1
    title_cell.alignment = Alignment(horizontal="left", vertical="center")  # Alineación
    title_cell.border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Definir los encabezados de la tabla
    headers = ['ITEM', 'DESCRIPCION DE PARTIDA', 'UNIDAD', 'CANTIDAD', 'MONEDA', 'P.U.', 'SUB TOTAL', 'TOTAL']
    
    # Añadir los encabezados de la tabla en la primera fila
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=2, column=col_num)
        cell.value = header
        cell.font = Font(name="Calibri", size=6, bold=True)  # Aplicar formato a los encabezados
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

    # Empezamos a agregar ítems debajo de los encabezados (en la fila 2)
    current_row = 3  # Fila donde comenzarán los ítems
    
    # Agregar los ítems por categoría
    for categoria, items in items_by_category.items():
        # Agregar el nombre de la categoría (puede ser una fila de texto o un título para separar categorías)
        category_cell = sheet.cell(row=current_row, column=1, value=f'{categoria}')
        category_cell.font = Font(name="Calibri", size=6, bold=True)  # Formato para la categoría
        category_cell.alignment = Alignment(horizontal="left", vertical="center")
        current_row += 1  # Aumentamos la fila para que los ítems vayan debajo de la categoría

        # Añadir los ítems en las filas correspondientes
        for item in items:
            subtotal = item.total_price
            row = [
                item.item.sap,                # ITEM
                item.item.description,        # DESCRIPCIÓN DE PARTIDA
                item.item.unit,               # UNIDAD
                item.quantity,                # CANTIDAD
                item.coin,                    # MONEDA
                item.item.price,              # P.U.
                subtotal,                     # SUB TOTAL
                subtotal,                     # TOTAL
            ]
            
            # Añadir la fila del ítem en la hoja
            for col_num, value in enumerate(row, 1):
                cell = sheet.cell(row=current_row, column=col_num, value=value)
                # Aplicar formato a las celdas de los ítems
                cell.font = Font(name="Calibri", size=6)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
            
            current_row += 1  # Avanzamos a la siguiente fila para el siguiente ítem

    # Ajustar el ancho de las columnas para que los datos sean legibles
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Obtener el nombre de la columna (letra)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = max_length + 2  # Un poco de espacio adicional para mejorar la legibilidad
        sheet.column_dimensions[column].width = adjusted_width



    # Ajustar el ancho de las columnas para que los datos sean legibles
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Obtener el nombre de la columna (letra)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column].width = adjusted_width


    # Ajustar ancho de las columnas
    for column in sheet.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value)  # Evitar valores vacíos
        adjusted_width = max_length + 2
        sheet.column_dimensions[column[0].column_letter].width = adjusted_width

    
def _create_quote(plantilla, budget):
    sheet = plantilla['COTIZACION']
    # Datos del cliente
    sheet['C18'] = f'{budget.client}'
    sheet['C19'] = f'{budget.client.primary_contact}'
    sheet['C20'] = f'{budget.client.email}'
    sheet['C21'] = f'{budget.client.phone}'

    # Información del presupuesto
    sheet['G20'] = f'{budget.budget_number}'
    sheet['G21'] = f'{budget.budget_date}'

    # Detalles de la cotización
    sheet['C27'] = f'{budget.budget_name}'
    sheet['G30'] = f'{budget.budget_final_price}'

    # Tiempos
    sheet['D35'] = f'{budget.budget_deliverytime}'
    sheet['D36'] = f'{budget.budget_servicetime}'
    sheet['D38'] = f'{budget.budget_warrantytime}'

def process_budget_excel(excel_file, budget_id):
    # Obtener la instancia de Budget por su ID
    budget = Budget.objects.get(id=budget_id)

    # Procesar el archivo Excel
    xls = pd.ExcelFile(excel_file)
    if 'listado' not in xls.sheet_names:
        raise ValueError("El archivo no contiene una hoja llamada 'listado'.")

    # Leer la hoja "listado" del archivo Excel
    df = pd.read_excel(xls, sheet_name='listado')

    # Verificar que las columnas esperadas existan
    expected_columns = ['DESCRIPCION DE PARTIDA', 'UND', 'CANT.', 'P.U.']
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("El archivo Excel no tiene el formato esperado.")

    # Iterar sobre cada fila y procesar los datos
    for index, row in df.iterrows():
        description = row['DESCRIPCION DE PARTIDA']
        unit = row['UND']
        quantity = row['CANT.']
        custom_price = row['P.U.']

        # Buscar el ítem en el catálogo por coincidencia exacta
        catalog_item = CatalogItem.objects.filter(description__iexact=description).first()

        # Si encuentra una coincidencia exacta, crear el BudgetItem
        if catalog_item:
            BudgetItem.objects.create(
                budget=budget,
                item=catalog_item,
                quantity=quantity,
                custom_price=custom_price,
                custom_price_per_day=catalog_item.price_per_day,  # Si es necesario
                unit=unit
            )
        else:
            # Si no se encuentra coincidencia exacta, continuar con el siguiente ítem
            print(f"No se encontró el ítem exacto para: {description}")
            continue

def determine_category(sap_code):
    """Determina la categoría del ítem basado en las primeras letras del código SAP."""
    if sap_code.startswith('HER'):
        return CatalogItem.Category.HERRAMIENTA
    elif sap_code.startswith('CON'):
        return CatalogItem.Category.CONSUMIBLE
    elif sap_code.startswith('MOB'):
        return CatalogItem.Category.MANODEOBRA
    elif sap_code.startswith('MAT'):
        return CatalogItem.Category.MATERIAL
    elif sap_code.startswith('EPPS'):
        return CatalogItem.Category.EPPS
    elif sap_code.startswith('EQU'):
        return CatalogItem.Category.EQUIPO
    else:
        return CatalogItem.Category.EQUIPO  # Asignar una categoría por defecto si no coincide

def process_sap_excel(excel_file, budget):
    # Cargar el archivo Excel y verificar que tiene la hoja esperada
    xls = pd.ExcelFile(excel_file)
    if 'listado' not in xls.sheet_names:
        raise ValueError("El archivo no contiene una hoja llamada 'listado'.")

    # Leer la hoja 'listado' en un DataFrame
    df = pd.read_excel(xls, sheet_name='listado')

    # Verificar que las columnas del archivo Excel coincidan con las esperadas
    expected_columns = ['Número de artículo', 'Descripción del artículo', 'Nombre de unidad de medida', 'Cantidad', 'Precio por unidad', 'Total (ML)', 'Moneda']
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("El archivo Excel no tiene el formato esperado.")

    # Función para convertir valores a Decimal, limpiando comas y símbolos no numéricos
    def safe_convert_to_decimal(value):
        try:
            # Si el valor es un string, eliminamos los caracteres no numéricos (como el símbolo y las comas)
            if isinstance(value, str):
                value = value.replace(",", "")  # Eliminar comas
                value = value.replace("S/", "").strip()  # Eliminar el símbolo S/
                value = value.replace("US$", "").strip()  # Eliminar el símbolo US$
            return Decimal(value)
        except (ValueError, decimal.InvalidOperation):
            return Decimal(0)

    # Aplicar conversión a las columnas necesarias
    df['Cantidad'] = df['Cantidad'].apply(safe_convert_to_decimal)
    df['Precio por unidad'] = df['Precio por unidad'].apply(safe_convert_to_decimal)
    df['Total (ML)'] = df['Total (ML)'].apply(safe_convert_to_decimal)

    # Agregar una columna de categoría al DataFrame usando la función determine_category
    df['Categoría'] = df['Número de artículo'].apply(determine_category)

    # Ordenar el DataFrame por la columna 'Categoría'
    df = df.sort_values(by='Categoría')

    # Inicializar sumas para los cálculos
    excel_total_sum = Decimal('0.00')
    processed_total_sum = Decimal('0.00')
    sap_codes_in_excel = set()

    with transaction.atomic():
        for index, row in df.iterrows():
            sap_code = row['Número de artículo']

            # Validar código SAP
            if pd.isna(sap_code) or pd.isnull(sap_code):
                print(f"Fila {index} sin código SAP. Saltando esta fila.")
                continue

            sap_code = str(sap_code).strip()
            sap_codes_in_excel.add(sap_code)

            # Obtener el resto de los datos
            description = row['Descripción del artículo']
            unit = row['Nombre de unidad de medida']
            quantity = row['Cantidad']
            coin = row['Moneda']
            custom_price = row['Precio por unidad']
            total_price = row['Total (ML)']
            excel_total_sum += total_price

            # Buscar o crear el CatalogItem correspondiente
            try:
                catalog_item = CatalogItem.objects.get(sap=sap_code)
                # Si ya existe el artículo, actualizar los detalles
                catalog_item.description = description
                catalog_item.unit = unit
                catalog_item.price = custom_price
                catalog_item.price_per_day = custom_price / Decimal(30) if custom_price else Decimal(0)
                catalog_item.save()
            except CatalogItem.DoesNotExist:
                # Si no existe el artículo, crear uno nuevo
                category = determine_category(sap_code)
                catalog_item = CatalogItem.objects.create(
                    sap=sap_code,
                    description=description,
                    unit=unit,
                    price=custom_price,
                    price_per_day=custom_price / Decimal(30) if custom_price else Decimal(0),
                    category=category
                )

            # Obtener o crear el BudgetItem correspondiente
            budget_item, created = BudgetItem.objects.get_or_create(
                budget=budget,
                item=catalog_item,
                coin=coin,
            )

            # Actualizar la información del BudgetItem
            budget_item.quantity = quantity
            budget_item.custom_price = custom_price
            budget_item.unit = unit
            budget_item.total_price = total_price
            budget_item.coin = coin  
            budget_item.save()

            processed_total_sum += budget_item.total_price
            print(f"Fila Excel {index}: SAP={sap_code}, Total Excel={total_price}, Total Procesado={budget_item.total_price}")

        # Eliminar los BudgetItems que no están en el archivo Excel
        current_sap_codes = set(budget.items.values_list('item__sap', flat=True))
        sap_codes_to_delete = current_sap_codes - sap_codes_in_excel

        if sap_codes_to_delete:
            items_to_delete = budget.items.filter(item__sap__in=sap_codes_to_delete)
            items_to_delete.delete()
            print(f"Se han eliminado {items_to_delete.count()} BudgetItems que ya no están en el Excel.")
        else:
            print("No hay BudgetItems para eliminar.")

        # Asignar directamente el total procesado al presupuesto
        budget.budget_price = processed_total_sum.quantize(Decimal('0.01'))
        budget.save()

        print(f"Presupuesto actualizado: Precio parcial={budget.budget_price}, Precio completo={budget.budget_final_price}")


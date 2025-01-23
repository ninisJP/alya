# See LICENSE file for copyright and license details.
"""
Budget views
"""
import re
import os
from decimal import Decimal

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db import models
from django.db import transaction
from django.http import FileResponse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from openpyxl import Workbook

from accounting_order_sales.models import SalesOrder, SalesOrderItem
from .forms import (
    BudgetEditNewForm,
    BudgetForm,
    BudgetItemFormSet,
    BudgetPlusForm,
    CatalogItemForm,
    SearchCatalogItemForm,
    NewBudgetItemForm,
    EditBudgetItemForm,
    BudgetUploadForm,
    ExcelUploadForm,
)
from .models import Budget, BudgetItem, CatalogItem
from .utils import (
    export_budget_report_to_excel,
    process_budget_excel,
    process_sap_excel
)


def index_budget(request):
    """
    Budget index
    """

    budgets = Budget.objects.all()
    form = BudgetPlusForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            budget = form.save()
            return redirect('detail_budget_plus', pk=budget.pk)

    return render(
        request,
        'index_budget.html',
        {'budgets': budgets, 'form': form}
    )


def edit_budget_item_htmx(request, item_id):
    """
    Edit budget item with htmx
    """

    item = get_object_or_404(BudgetItem, id=item_id)

    if request.method == 'POST':
        form = EditBudgetItemForm(request.POST, instance=item)

        if form.is_valid():
            # Update total price
            quantity = form.cleaned_data.get('quantity')
            custom_price = form.cleaned_data.get('custom_price') or item.item.price  # Usar precio del catálogo si está vacío
            custom_price_per_day = form.cleaned_data.get('custom_price_per_day') or item.item.price_per_day

            # Total price by item category
            if item.item.category in [CatalogItem.Category.HERRAMIENTA, CatalogItem.Category.MANODEOBRA, CatalogItem.Category.EPPS]:
                item.total_price = (
                    Decimal(custom_price_per_day) *
                    Decimal(quantity) *
                    Decimal(item.budget.budget_days)
                )
            else:
                item.total_price = Decimal(custom_price) * Decimal(quantity)

            form.save()

            return render(request, 'budget/item_row.html', {'item': item})
    else:
        form = EditBudgetItemForm(instance=item)

    return render(
        request,
        'budget/edit_item_form.html',
        {'form': form, 'item': item}
    )


def upload_budget_excel(request, budget_id):
    """
    Upload excel in budget
    """

    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']

        # temporal save
        # fs = FileSystemStorage()
        # filename = fs.save(excel_file.name, excel_file)
        # uploaded_file_url = fs.url(filename)

        process_budget_excel(excel_file, budget_id)

        return redirect('detail_budget', pk=budget_id)

    return render(
        request,
        'budget/upload_excel.html',
        {'budget_id': budget_id}
    )


def upload_sap_excel(request, budget_id):
    """
    Upload excel sap
    """

    budget = get_object_or_404(Budget, id=budget_id)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            process_sap_excel(excel_file, budget)
            return redirect('detail_budget_plus', pk=budget_id)
        except Exception:
            return redirect('detail_budget_plus', pk=budget_id)

    return redirect('detail_budget_plus', pk=budget_id)


def delete_budget(request, pk):
    """
    Remove budget.
    """

    budget = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        budget.delete()
        messages.success(
            request,
            'El presupuesto ha sido eliminado exitosamente.'
        )
        return redirect('index_budget')

    return render(request, 'budget/delete_budget.html', {'budget': budget})


def duplicate_budget(request, pk):
    """
    Duplicate a budget. Add duplicate in the name.
    """

    original_budget = get_object_or_404(Budget, pk=pk)

    duplicated_budget = Budget.objects.get(pk=original_budget.pk)
    duplicated_budget.pk = None
    duplicated_budget.budget_name = f"{original_budget.budget_name} (Duplicado)"
    duplicated_budget.save()

    # Copy the items
    for item in original_budget.items.all():
        duplicated_item = BudgetItem.objects.get(pk=item.pk)
        duplicated_item.pk = None
        duplicated_item.budget = duplicated_budget
        duplicated_item.save()

    return redirect(
        'detail_budget_plus',
        pk=duplicated_budget.pk
    )


def create_sales_order_from_budget(request, budget_id):
    """
    Create sales order from budget (Duplicate items)

    TODO: make a relation beetween budget, included items, and sales order.
    """

    budget = get_object_or_404(Budget, id=budget_id)
    if not budget.budget_number:
        messages.error(
            request,
            "El presupuesto no tiene un número SAP válido. por favor colocar código SAP"
        )
        return redirect('detail_budget_plus', pk=budget_id)

    # Check sap code is unique
    existing_sales_order = SalesOrder.objects.filter(
        sapcode=budget.budget_number
    ).first()

    # Atomic transaction
    with transaction.atomic():
        if existing_sales_order:
            # Update sales order
            existing_sales_order.days = budget.budget_days
            existing_sales_order.save()

            sap_codes_in_budget = set()

            for budget_item in budget.items.all():
                sap_code = str(budget_item.item.sap).strip().upper()
                sap_codes_in_budget.add(sap_code)

                price_with_igv = (budget_item.custom_price or budget_item.item.price) * Decimal('1.18')
                total_price_with_igv = budget_item.total_price * Decimal('1.18') if budget_item.total_price else Decimal('0.00')

                sales_order_item = existing_sales_order.items.filter(sap_code__iexact=sap_code).first()
                if sales_order_item:
                    # Update sales order
                    sales_order_item.amount = budget_item.quantity
                    sales_order_item.price = price_with_igv
                    sales_order_item.price_total = total_price_with_igv
                    sales_order_item.unit_of_measurement = budget_item.unit or budget_item.item.unit
                    sales_order_item.category = budget_item.item.category
                    sales_order_item.description = budget_item.item.description
                    sales_order_item.custom_quantity = budget_item.custom_quantity
                    sales_order_item.custom_price_per_hour = budget_item.custom_price_per_hour
                    sales_order_item.save()
                    sales_order_item.update_remaining_requirement()
                else:
                    # Create new sales order
                    new_item = SalesOrderItem.objects.create(
                        salesorder=existing_sales_order,
                        sap_code=sap_code,
                        description=budget_item.item.description,
                        amount=budget_item.quantity,
                        price=price_with_igv,
                        price_total=total_price_with_igv,
                        unit_of_measurement=budget_item.unit or budget_item.item.unit,
                        category=budget_item.item.category,
                        custom_quantity=budget_item.custom_quantity,
                        custom_price_per_hour=budget_item.custom_price_per_hour,
                    )
                    new_item.update_remaining_requirement()

            # get items's sap code
            sap_codes_in_sales_order = set(
                str(item.sap_code).strip().upper()
                for item in existing_sales_order.items.all()
            )

            # Get SAP of item list to remove
            sap_codes_to_delete = (
                sap_codes_in_sales_order -
                sap_codes_in_budget
            )

            if sap_codes_to_delete:
                # Remove items
                items_to_delete = existing_sales_order.items.filter(
                    sap_code__in=sap_codes_to_delete
                )
                # count_deleted = items_to_delete.count()
                items_to_delete.delete()
        else:
            # Create sales order
            sales_order = SalesOrder.objects.create(
                sapcode=budget.budget_number,
                project=None,
                detail=f"Orden basada en el presupuesto {budget.budget_name}",
                date=budget.budget_date,
                days=budget.budget_days,
            )

            for budget_item in budget.items.all():
                sap_code = str(budget_item.item.sap).strip().upper()
                price_with_igv = (budget_item.custom_price or budget_item.item.price) * Decimal('1.18')
                total_price_with_igv = budget_item.total_price * Decimal('1.18') if budget_item.total_price else Decimal('0.00')

                new_item = SalesOrderItem.objects.create(
                    salesorder=sales_order,
                    sap_code=sap_code,
                    description=budget_item.item.description,
                    amount=budget_item.quantity,
                    price=price_with_igv,
                    price_total=total_price_with_igv,
                    unit_of_measurement=budget_item.unit or budget_item.item.unit,
                    category=budget_item.item.category,
                    custom_quantity=budget_item.custom_quantity,
                    custom_price_per_hour=budget_item.custom_price_per_hour,
                )
                new_item.update_remaining_requirement()

    return redirect('index_budget')


def export_budget_report(request, pk):
    """
    Create excel report of budget
    """

    return export_budget_report_to_excel(request, pk)


def download_template(request):
    """
    Download the excel template for budget
    """

    file_path = os.path.join(settings.BASE_DIR, 'static', 'listado.xlsx')
    if os.path.exists(file_path):
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="listado.xlsx"'
        return response
    else:
        return HttpResponse(
            "El archivo no se encuentra disponible.",
            status=404
        )


def catalog(request):
    """
    Catalog
    """

    form = CatalogItemForm()
    search_form = SearchCatalogItemForm()

    catalogs = cache.get('catalog_items')

    # Check cache
    if not catalogs:
        catalogs = CatalogItem.objects.all()
        cache.set('catalog_items', catalogs, timeout=3600)

    # Paginator
    paginator = Paginator(catalogs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'search': search_form,
        'catalogs': page_obj,
    }

    return render(request, 'catalog/home.html', context)


def catalog_item_search(request):
    """
    Search catalog item.
    """

    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        term = request.GET.get('term', '')
        items = CatalogItem.objects.all()

        if term:
            items = items.filter(
                models.Q(description__icontains=term) |
                models.Q(sap__icontains=term)
            )

        items = items.order_by('description')

        paginator = Paginator(items, 100)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        results = []
        for item in page_obj:
            results.append({
                'id': item.id,
                'text': f'{item.sap} - {item.description}',
            })

        return JsonResponse(
            {
                'results': results,
                'pagination': {
                    'more': page_obj.has_next()
                }
            }
        )

    return JsonResponse({'results': []})


def catalog_edit(request, catalog_id):
    """
    Edit catalog
    """

    catalog = get_object_or_404(CatalogItem, id=catalog_id)

    if request.method == 'POST':
        form = CatalogItemForm(request.POST, instance=catalog)
        if form.is_valid():
            form.save()
            # Después de guardar, renderizar el lista ítem
            catalog = get_object_or_404(CatalogItem, id=catalog_id)
            return render(
                request,
                'catalog/list_element.html',
                {'catalog': catalog}
            )
    else:
        form = CatalogItemForm(instance=catalog)

    context = {'form': form, 'catalog': catalog}
    return render(request, 'catalog/edit.html', context)


def catalog_new(request):
    """
    Create a new catalog
    """

    context = {}
    if request.method == 'POST':
        form = CatalogItemForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['form'] = CatalogItemForm()

    return render(request, 'catalog/form.html', context)


def catalog_search(request):
    """
    Search catalog
    """

    query = request.GET.get('q', '')

    if query:
        catalogs = CatalogItem.objects.filter(Q(sap__contains=query)).order_by('-id')
    else:
        catalogs = CatalogItem.objects.all().order_by('-id')

    context = {'catalogs': catalogs, 'form': CatalogItemForm()}
    return render(request, 'catalog/list.html', context)


def upload_excel(request):
    """
    Upload excel
    """

    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            try:
                # Check file format
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    messages.error(
                        request,
                        "Solo se permiten archivos .csv y .xlsx."
                    )
                    return redirect('budget_catalog_excel')

                if df.empty:
                    messages.error(request, "El archivo está vacío.")
                    return redirect('budget_catalog_excel')

                required_columns = [
                    'Número de artículo',
                    'Descripción del artículo',
                    'Grupo de artículos',
                    'Unidad de medida de inventario',
                    'Último precio de compra'
                ]
                missing_columns = [
                    col for col in required_columns if col not in df.columns
                ]
                if missing_columns:
                    return redirect('budget_catalog_excel')

                items_to_create = []

                with transaction.atomic():
                    for _, row in df.iterrows():
                        try:
                            if pd.isnull(row['Número de artículo']) or pd.isnull(row['Descripción del artículo']):
                                continue

                            sap = str(
                                row['Número de artículo']
                            ).strip()
                            description = str(
                                row['Descripción del artículo']
                            ).strip()
                            category = str(
                                row['Grupo de artículos']
                            ).strip()
                            unit = str(row['Unidad de medida de inventario']).strip() if pd.notnull(row['Unidad de medida de inventario']) else 'UND'

                            price_str = str(
                                row['Último precio de compra']
                            ).strip()
                            price_cleaned = re.sub(
                                r'[^\d.,]',
                                '',
                                price_str
                            ).replace(',', '')
                            price = float(price_cleaned) if price_cleaned else 0.0

                            item, created = CatalogItem.objects.update_or_create(
                                sap=sap,
                                defaults={
                                    'description': description,
                                    'category': category,
                                    'unit': unit,
                                    'price': price,
                                    'price_per_day': 0.0
                                }
                            )
                            items_to_create.append(item)

                        except Exception as e:
                            print(f"Error procesando la fila: {e}")
                            continue

                if items_to_create:
                    CatalogItem.objects.bulk_create(
                        items_to_create,
                        ignore_conflicts=True
                    )

                return redirect('budget_catalog_excel')

            except pd.errors.ParserError:
                return redirect('budget_catalog_excel')

            except ValueError:
                return redirect('budget_catalog_excel')

            except KeyError:
                return redirect('budget_catalog_excel')

            except Exception:
                return redirect('budget_catalog_excel')

    else:
        form = ExcelUploadForm()

    return render(request, 'upload_excel.html', {'form': form})


def export_catalog(request):
    """
    Export catalog to excel
    """

    wb = Workbook()
    ws = wb.active
    ws.title = "Catalogo"

    ws.append(
        [
            'Número de artículo',
            'Descripción del artículo',
            'Grupo de artículos',
            'Unidad de medida de inventario',
            'Último precio de compra',
        ]
    )

    catalog_items = CatalogItem.objects.all()
    for item in catalog_items:
        ws.append(
            [item.sap, item.description, item.category, item.unit, item.price]
        )

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="catalogo.xlsx"'
    wb.save(response)

    return response

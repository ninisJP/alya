from django.shortcuts import redirect, render, get_object_or_404
from .forms import BrandForm, TypeForm, SubtypeForm, ItemForm, SearchItemForm
from .models import Brand, Type, Subtype, Item
from .utils import sort_item, search_item
from alya import utils
from alya.forms import SearchForm


def index(request):
    return render(request, 'logistic_inventory_sidebar.html')

def brand(request):
    context = {'form': BrandForm(), 'search': SearchForm()}
    return render(request, 'inventory/brand.html', context)

def brand_edit(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    if request.method == 'GET':
        form = BrandForm(instance=brand)
        context = {
                'form': form,
                'brand': brand,
                }
        return render(request, 'inventory/brand_edit.html', context)
    elif request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
            context = {
                    'form': form,
                    'brand': brand,
                    }
        context['status'] = status
        return render(request, 'inventory/brand_edit.html', context)
    return HttpResponse(status=405)

def brand_new(request):
    context = {}
    if request.method == 'POST':
        form = BrandForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['form'] = BrandForm()

    return render(request, 'inventory/brand_form.html', context)

def brand_search(request):
    context = {}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            status, brands = utils.search_model(Brand.objects.all(), 'name', form.cleaned_data['name'])
            if brands != {} :
                brands = brands.order_by('name')

            context['brands'] = brands
            context['search_status'] = status

    context['search'] = SearchForm()
    return render(request, 'inventory/brand_list.html', context)

def item(request):
    context = {'form': ItemForm(), 'search': SearchItemForm()}
    return render(request, 'inventory/item.html', context)

def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'GET':
        form = ItemForm(instance=item)
        context = {
                'form': form,
                'item': item,
                }
        return render(request, 'inventory/item_edit.html', context)
    elif request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
            context = {
                    'form': form,
                    'item': item,
                    }
        context['status'] = status
        return render(request, 'inventory/item_edit.html', context)
    return HttpResponse(status=405)

def item_new(request):
    context = {}
    if request.method == 'POST':
        form = ItemForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['form'] = ItemForm()

    return render(request, 'inventory/item_form.html', context)

def item_search(request):
    context = {}
    if request.method == 'POST':
        form = SearchItemForm(request.POST)
        if form.is_valid():

            # Search items
            status, items = search_item(Item.objects.all(), form)

            # Sort
            items = sort_item(items)

            context['items'] = items
            context['search_status'] = status

    context['search'] = SearchItemForm()
    return render(request, 'inventory/item_list.html', context)

def subtype(request):
    context = {'form': SubtypeForm(), 'search': SearchForm()}
    return render(request, 'inventory/subtype.html', context)

def subtype_edit(request, subtype_id):
    subtype = get_object_or_404(Subtype, id=subtype_id)
    print(subtype_id)
    if request.method == 'GET':
        form = SubtypeForm(instance=subtype)
        context = {
                'form': form,
                'subtype': subtype,
                }
        return render(request, 'inventory/subtype_edit.html', context)
    elif request.method == 'POST':
        form = SubtypeForm(request.POST, instance=subtype)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
            context = {
                    'form': form,
                    'subtype': subtype,
                    }
        context['status'] = status
        return render(request, 'inventory/subtype_edit.html', context)
    return HttpResponse(status=405)

def subtype_new(request):
    context = {}
    if request.method == 'POST':
        form = SubtypeForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['form'] = SubtypeForm()

    return render(request, 'inventory/subtype_form.html', context)

def subtype_search(request):
    context = {}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            status, subtypes = utils.search_model(Subtype.objects.all(), 'name', form.cleaned_data['name'])
            if subtypes != {} :
                subtypes = subtypes.order_by('name')

            context['subtypes'] = subtypes
            context['search_status'] = status

    context['search'] = SearchForm()
    return render(request, 'inventory/subtype_list.html', context)

def type(request):
    context = {'form': TypeForm(), 'search': SearchForm()}
    return render(request, 'inventory/type.html', context)

def type_edit(request, type_id):
    ttype = get_object_or_404(Type, id=type_id)
    if request.method == 'GET':
        form = TypeForm(instance=ttype)
        context = {
                'form': form,
                'type': ttype,
                }
        return render(request, 'inventory/type_edit.html', context)
    elif request.method == 'POST':
        form = TypeForm(request.POST, instance=ttype)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
            context = {
                    'form': form,
                    'type': ttype,
                    }
        context['status'] = status
        return render(request, 'inventory/type_edit.html', context)
    return HttpResponse(status=405)

def type_new(request):
    context = {}
    if request.method == 'POST':
        form = TypeForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['form'] = TypeForm()

    return render(request, 'inventory/type_form.html', context)

def type_search(request):
    context = {}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            status, types = utils.search_model(Type.objects.all(), 'name', form.cleaned_data['name'])
            if types != {} :
                types = types.order_by('name')

            context['types'] = types
            context['search_status'] = status

    context['search'] = SearchForm()
    return render(request, 'inventory/type_list.html', context)

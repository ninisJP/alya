from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse

from .forms import BrandForm, TypeForm, SubtypeForm, ItemForm, SearchItemForm
from .models import Brand, Type, Subtype, Item
from .utils import sort_item, search_item
from alya import utils
from alya.forms import SearchForm


def index(request):
    return render(request, 'logistic_inventory_sidebar.html')

def brand(request):
    context = {'form': BrandForm(), 'search': SearchForm()}
    context['brands'] = Brand.objects.all()
    return render(request, 'inventory/brand/home.html', context)

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

    return render(request, 'inventory/brand/form.html', context)

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
    return render(request, 'inventory/brand/list.html', context)

def item(request):
    context = {'form': ItemForm(), 'search': SearchItemForm()}
    context['items'] = Item.objects.all()
    return render(request, 'inventory/item.html', context)

def item_new(request):
    context = {}
    if request.method == 'POST':
        form = ItemForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['types'] = Type.objects.all()
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
    context['subtypes'] = Subtype.objects.all()
    return render(request, 'inventory/subtype/home.html', context)

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

    return render(request, 'inventory/subtype/form.html', context)

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
    return render(request, 'inventory/subtype/list.html', context)

def type(request):
    context = {'form': TypeForm(), 'search': SearchForm()}
    context['types'] = Type.objects.all()
    return render(request, 'inventory/type/home.html', context)

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

    return render(request, 'inventory/type/form.html', context)

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
    return render(request, 'inventory/type/list.html', context)

def get_all_subtypes(request):
    form = ItemForm(request.GET)
    return HttpResponse(form["subtype"])

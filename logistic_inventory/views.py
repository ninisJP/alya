from django.shortcuts import render

from .forms import BrandForm, TypeForm, SubtypeForm, ItemForm
from .models import Brand, Type, Subtype, Item

from alya import utils
from alya.forms import SearchForm


def index(request):
    return render(request, 'logistic_inventory_sidebar.html')

def brand(request):
    context = {'form': BrandForm(), 'search': SearchForm()}
    return render(request, 'inventory/brand.html', context)

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
            context['brands'] = brands
            context['search_status'] = status

    context['search'] = SearchForm()
    return render(request, 'inventory/brand_list.html', context)

def item(request):
    context = {'form': ItemForm(), 'search': SearchForm()}
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

    context['form'] = ItemForm()

    return render(request, 'inventory/item_form.html', context)

def item_search(request):
    context = {}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            status, items = utils.search_model(Item.objects.all(), 'description', form.cleaned_data['name'])
            context['items'] = items
            context['search_status'] = status

    context['search'] = SearchForm()
    return render(request, 'inventory/item_list.html', context)

def subtype(request):
    context = {'form': SubtypeForm(), 'search': SearchForm()}
    return render(request, 'inventory/subtype.html', context)

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
            context['subtypes'] = subtypes
            context['search_status'] = status

    context['search'] = SearchForm()
    return render(request, 'inventory/subtype_list.html', context)

def type(request):
    context = {'form': TypeForm(), 'search': SearchForm()}
    return render(request, 'inventory/type.html', context)

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
            context['types'] = types
            context['search_status'] = status

    context['search'] = SearchForm()
    return render(request, 'inventory/type_list.html', context)

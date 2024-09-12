from django.shortcuts import render

from .forms import BrandForm, SearchForm
from .models import Brand
from . import utils


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
    return render(request, 'inventory/item.html')

def subtype(request):
    return render(request, 'inventory/subtype.html')

def type(request):
    return render(request, 'inventory/type.html')

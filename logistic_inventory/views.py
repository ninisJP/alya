from django.shortcuts import render

from .forms import BrandForm
from .models import Brand


def index(request):
    return render(request, 'logistic_inventory_sidebar.html')

def brand(request):
    brands = Brand.objects.all().order_by('name')
    context = {'form': BrandForm(), 'brands': brands}
    return render(request, 'inventory/brand.html', context)

def brand_new(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            brands = Brand.objects.all().order_by('name')
            context = {'brands': brands }
            return render(request, 'inventory/brand_list.html', context)
    else:
        form = BrandForm()

    return render(request, 'inventory/brand_form.html', {'form': form})

def item(request):
    return render(request, 'inventory/item.html')

def subtype(request):
    return render(request, 'inventory/subtype.html')

def type(request):
    return render(request, 'inventory/type.html')

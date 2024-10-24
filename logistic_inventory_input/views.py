from django.shortcuts import render

from logistic_inventory_output.models import InventoryOutput

def input_index(request):
	context = {}
	context['outputs'] = InventoryOutput.objects.filter(returned=False)
	print(context['outputs'])
	return render(request, 'input/home.html', context)

def input_new(request, output_pk):
	return

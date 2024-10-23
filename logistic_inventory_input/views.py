from django.shortcuts import render


from .utils import get_inputs


def input_index(request):
    outputs = get_inputs()
    context = {}
    context['outputs'] = outputs
    return render(request, 'input/home.html', context)

from django.shortcuts import render

from .forms import SearchGuideForm
from .utils import search_guide

def index(request):
	context = {}
	context['search'] = SearchGuideForm()
	return render(request, 'register/home.html', context)

def search(request):
	context = {}
	if request.method == 'POST':
		form = SearchGuideForm(request.POST)
		if form.is_valid():
			context_tmp = search_guide(form)
			context.update(context_tmp)

	context['search'] = SearchGuideForm()
	return render(request, 'register/list.html', context)

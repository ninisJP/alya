from django.shortcuts import render
from .forms import ClientForm

# Create your views here.
def index_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'partials/success_client.html')
        return render(request, 'partials/failure_client.html')
            
    form = ClientForm()
    context = {'form': form}
    return render(request, 'index_client.html', context)
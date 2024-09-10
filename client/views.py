from django.shortcuts import render
from .forms import ClientForm
from .models import Client

# Create your views here.
def index_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            context = {'client': client}
            return render(request, 'partials/client_list.html', context)
        return render(request, 'partials/failure_client.html')

    form = ClientForm()
    context = {'form': form, 'clients': Client.objects.all()}
    return render(request, 'index_client.html', context)

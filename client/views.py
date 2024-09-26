from django.shortcuts import render
from .forms import ClientForm
from .models import Client
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_htmx.http import HttpResponseLocation, HttpResponseClientRedirect

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

def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'GET':
        form = ClientForm(instance=client)
        return render(request, 'partials/edit_client.html', {'form': form, 'client': client})
    elif request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            client = get_object_or_404(Client, id=client_id)
            return render(request, 'partials/client_list.html', {'client': client})
    return HttpResponse(status=405)

def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'DELETE':
        client.delete()
        return render(request, 'partials/client_list.html')
    return HttpResponse(status=405)

def nav_client(request):
    if request.htmx:
        destiny = request.GET.get('destiny')
        if destiny == 'contrato':
            return HttpResponseLocation('/clientes/crm/contrato/',)
        elif destiny == 'proyectos':
            return HttpResponseLocation('/clientes/crm/oportunidad/',)
        else:
            return HttpResponseLocation('/default/')
    else:
        return render(request, 'nav_client.html')

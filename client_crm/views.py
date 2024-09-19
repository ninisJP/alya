from django.shortcuts import render, redirect
from .models import Contract
from .forms import ContractForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# Contrat Create
def index_contract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)  # Incluir request.FILES para manejar archivos
        if form.is_valid():
            print("Formulario válido. Archivo:", request.FILES.get('contract_pdf'))
            contract = form.save()

            if request.headers.get('HX-Request'):
                return render(request, 'contract/contract_list.html', {'contract': contract})

            context = {'form': ContractForm(), 'contracts': Contract.objects.all()}
            return render(request, 'contract/contract.html', context)
        
        if request.headers.get('HX-Request'):
            return HttpResponse("Error en el formulario", status=400)

        return render(request, 'client/partials/failure_client.html')

    form = ContractForm()
    context = {'form': form, 'contracts': Contract.objects.all().order_by('-id'),'pagina_activa': 'contratos'
}
    return render(request, 'contract/contract.html', context)

# Contract Edit
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            contract = form.save()

            if request.headers.get('HX-Request'):
                contracts = Contract.objects.all().order_by('-id')
                return render(request, 'contract/contract_list.html', {'contract': contract, 'contracts': contracts})

            return redirect('index_contract')  

        if request.headers.get('HX-Request'):
            return HttpResponse("Error en el formulario", status=400)

        return render(request, 'client/partials/failure_client.html')

    form = ContractForm(instance=contract)
    contracts = Contract.objects.all().order_by('-id')  
    context = {'form': form, 'contracts': contracts}
    return render(request, 'contract/contract_edit.html', context)


# Contract Delete
def delete_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        contract.delete()

        if request.headers.get('HX-Request'):
            return HttpResponse(status=204) 

        return redirect('index_contract')
    
    return render(request, 'contract/contract_delete.html', {'contract': contract})

def opportunity(request):
    return render(request, 'opportunity/opportunity.html')

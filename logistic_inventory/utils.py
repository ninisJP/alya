from django.shortcuts import get_object_or_404

import re

from alya import utils

from .models import Item


def sort_item(model):
    # Get keys to sort
    sort_type = []
    for item in model :
        element = {
                "type" : str(item.subtype.type),
                "subtype" : str(item.subtype),
                "brand" : str(item.brand),
                "description" : item.description,
                "id" : item.pk,
                }
        sort_type.append(element)

    # Sort
    sort_type = sorted(sort_type, key=lambda x: (x['type'], x['subtype'], x['brand'], x['description']))

    model_list = []
    for item in sort_type :
        model_list.append(model.filter(pk__in=str(item["id"])).first())

    return model_list

def search_item(model_all, form):

    model_list = model_all

    if form.cleaned_data['type'] :
        type = form.cleaned_data['type']
        # Get keys to sort
        r = re.compile(".*type.*", re.IGNORECASE)

        list_type = []
        for item in model_list :
            item_type = str(item.subtype.type)
            find_type = re.search(type, item_type, re.IGNORECASE)
            if find_type != None :
                list_type.append(item.pk)
        model_list = model_all.filter(pk__in=list_type)

    if form.cleaned_data['description'] :
        status, model_list = utils.search_model(model_list, 'description', form.cleaned_data['description'], accept_all=True)

    if form.cleaned_data['sap'] :
        sap = form.cleaned_data['sap']
        # Get keys to sort
        r = re.compile(".*sap.*", re.IGNORECASE)

        list_sap = []
        for item in model_list :
            item_sap = str(item.item.sap)
            find_sap = re.search(sap, item_sap, re.IGNORECASE)
            if find_sap != None :
                list_sap.append(item.pk)
        model_list = model_all.filter(pk__in=list_sap)

    status = 0
    if len(model_list) == 0:
        status = -2

    return status, model_list

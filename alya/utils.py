import re

# Example: search_model(Brand.objects.all(), 'name', form.cleaned_data['name'])
# Return status, list_model
def search_model(model_all, column, name, accept_all=False):
    # Minimal word's length is 4
    if not accept_all :
        if len(name) < 4 :
            return -1, {}

    model_list = list(model_all.values())

    regex_str = str(name)

    # If void
    if regex_str == "" :
        return 0, model_all

    list_find = []
    for element in model_list:
        match = re.findall(regex_str, str(element[column]), re.IGNORECASE)
        match = ''.join(match)
        if len(match):
            list_find.append(element)

    # Get model id
    list_id = []
    for item in list_find :
        id_name =list(item.keys())[0]
        list_id.append(item[id_name])

    # Get model
    model_list = model_all.filter(pk__in=list_id)

    if len(model_list) == 0:
        return -2, model_list
    return 0, model_list

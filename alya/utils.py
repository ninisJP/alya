import re

# Example: search_model(Brand.objects.all(), 'name', form.cleaned_data['name'])
# Return status, list_model
def search_model(model_all, column, name, accept_all=False):
    # Minimal word's length is 4
    if not accept_all :
        if len(name) < 4 :
            return -1, {}
    # Get all element
    model_list = list(model_all.values_list(column))
    # Convert to str list
    model_list_str = []
    for element in model_list:
        model_list_str.append(element[0])
    # Regex
    r = re.compile(".*"+str(name)+".*", re.IGNORECASE)
    list_new = list(filter(r.match, model_list_str))

    # Get model's element
    model_list = []
    for element in list_new :
        parameter = {column:element}
        model_list.append(model_all.get(**parameter))

    # Get model id
    list_id = []
    for element in model_list :
        list_id.append(element.id)

    # Get model
    model_list = model_all.filter(pk__in=list_id)

    if len(model_list) == 0:
        return -2, model_list
    return 0, model_list

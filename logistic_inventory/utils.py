import re

# Example: search_model(Brand.objects.all(), 'name', form.cleaned_data['name'])
def search_model(model_all, column, name):
    # Minimal word's length is 4
    if len(name) < 4 :
        return -1, {}
    # Get all element
    model_list = list(model_all.values_list(column))
    # Convert to str list
    model_list_str = []
    for element in model_list:
        model_list_str.append(element[0])
    # Regex
    r = re.compile(name)
    list_new = list(filter(r.match, model_list_str))

    # Get model's element
    model_list = []
    for element in list_new :
        model_list.append(model_all.get(name=element))
    if len(model_list) == 0:
        return -2, model_list
    return 0, model_list

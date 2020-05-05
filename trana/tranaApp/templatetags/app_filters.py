from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    if type(dictionary) is dict:
        return dictionary.get(key)
    return None


@register.filter
def get_co(dictionary, key):
    if type(dictionary) is dict:
        if key == "lat":
            return dictionary.get("location")[0]
        else:
            return dictionary.get("location")[1]

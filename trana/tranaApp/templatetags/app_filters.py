from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    if type(dictionary) is dict:
        return dictionary.get(key)
    return None

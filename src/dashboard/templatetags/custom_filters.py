from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """
    Retourne une liste de chaînes séparées par le délimiteur spécifié.
    Usage: {{ "a,b,c"|split:"," }}
    """
    if value is None:
        return []
    return value.split(arg) 
# filters.py
from django import template

register = template.Library()

@register.filter
def get_week_day(jour):
    return (jour % 7) + 1
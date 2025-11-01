from django import template
from Tickets.Choices import PRIORITY_COLORS

register = template.Library()

@register.filter
def get_priority_color(priority):
    return PRIORITY_COLORS.get(priority, '#6c757d')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')
from django import template
from Tickets.Choices import *

register = template.Library()

@register.filter
def get_priority_color(priority):
    return PRIORITY_COLORS.get(priority, '#6c757d')

@register.filter
def get_status_color(status):
    return STATUS_COLORS.get(status, '#6c757d')

@register.filter
def get_department_color(department):
    return DEPARTMENT_COLORS.get(department, '#6c757d')

@register.filter
def get_response_status_color(response_status):
    return RESPONSE_STATUS_COLORS.get(response_status, '#6c757d')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')
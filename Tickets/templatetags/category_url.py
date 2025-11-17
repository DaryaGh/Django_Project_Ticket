from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def category_tickets_url(category_id):
    return reverse('tickets') + f'?category={category_id}'
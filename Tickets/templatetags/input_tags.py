from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def input_tag(name, input_type='text', value='', placeholder='', css_class='form-control', required=False):
    required_attr = 'required' if required else ''

    html = f'''
    <input type="{input_type}" 
           name="{name}" 
           id="id_{name}"
           value="{value}" 
           placeholder="{placeholder}" 
           class="{css_class}" 
           {required_attr}>
    '''
    return mark_safe(html)
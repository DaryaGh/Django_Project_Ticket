from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def alert(message, color='info', dismissible=True):
    dismissible_html = ''
    if dismissible:
        dismissible_html = ' alert-dismissible fade show'
        close_button = '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>'
    else:
        close_button = ''

    html = f'''
    <div class="alert alert-{color}{dismissible_html}" role="alert">
        {message}
        {close_button}
    </div>
    '''
    return mark_safe(html)

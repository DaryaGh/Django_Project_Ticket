from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def widget_card(title , count,color='primary',url=None,icon='',extra_class='' , size='sm'):
    """
       usage:
           {% widget_card title="Total" count=5 url=tickets color="warming" icon='pencil' %}
       """

    esc = conditional_escape

    cls = f'card {esc(extra_class)}'.strip()

    title_html = ""
    if title:
        title_html = format_html('<h3 class="card-title mb-3">{}</h3>', title)

    count_html = ""
    if count :
        count_html = format_html('<p class="card-text"><span class="badge bg-{} fs-1">{}</span></p>',esc(color) ,count)


    if color and color not in ('primary', 'secondary', 'dark', 'light', 'danger', 'info', 'success', 'warning'):
        color = 'primary'

    icon_html = ''
    if icon:
        icon_html = format_html('<i class="bi {} me-1"></i>', esc(icon))

    link_html = ''
    if url is not None:
        link_html = format_html('<a href="{}" class="btn btn-outline-{}">{}</a>',esc(url),esc(color),"Read More")
    # return format_html('<div class="card card-body {}">{} {} {} {}</div>',cls, title_html,count_html, icon_html,link_html)
    return format_html('<div class="{}"><div class="card-body">{} {} {} {}</div></div>',cls,title_html,count_html,link_html,icon_html)


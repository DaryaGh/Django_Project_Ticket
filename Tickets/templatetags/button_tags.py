from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def button(label="Ok",
           url=None,
           color='primary',
           # outline=True,
           icon=None,
           type='link',
           size='sm',
           extra_class ='',
           confirm=None):
    """
    usage:
        {% button 'Edit' ticket.get_edit_url color='warming' icon='bi-pencil'%}
        {% button 'save' type='submit' color='primary' icon='bi-check-lg'%}
        {% button "delete" ticket.get_delete_url color='danger' icon='bi-trash' confirm=''%}
    """

    esc  = conditional_escape

    size_cls = f' btn-{size}' if size in ('sm', 'lg') else ''

    if color and color not in ('primary', 'secondary','dark','light','danger','info','success', 'warning'):
        color = 'primary'

    cls = f'btn btn-{esc(color)}{size_cls} {esc(extra_class)}'.strip()

    # چون تگ هست و بخواهیم به صورت رشته در بیاریم
    icon_html = ''
    if icon:
        icon_html = format_html('<i class="bi {} me-1"></i>', esc(icon))

    if url and type == 'link':
        return format_html('<a href="{}" class="{}">{}</a>',esc(url),cls,mark_safe(icon_html + esc(label)))

    else:

        confirm_attr = ''
        if confirm:
            confirm_js = f'return confirm({format_html("{}", esc(confirm))});'
            confirm_attr = format_html('onclick="{}"',mark_safe(confirm_js))
        btn_type = esc(type) if type else 'submit'
        return format_html('<button type="{}" class="{}"{}>{}</button>', btn_type,cls,confirm_attr,mark_safe(icon_html + esc(label)))

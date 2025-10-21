from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def button(label="Ok",
           url=None,
           color='primary',
           icon=None,
           type='link',
           size='sm',
           extra_class='',
           confirm=None,
           modal_target=None,
           outline=False,
           **attrs):
    """
    usage:
        {% button 'Edit' ticket.get_edit_url color='warning' icon='bi-pencil' %}
        {% button 'save' type='submit' color='primary' icon='bi-check-lg' %}
        {% button "delete" color='danger' icon='bi-trash3' modal_target='#deleteModal' data_ticket_id=ticket.id data_ticket_number=ticket.id %}
    """

    esc = conditional_escape

    if outline:
        outline = f'btn-outline-{color}'
    else:
        outline = f'btn-{color}'

    size_cls = f' btn-{size}' if size in ('sm', 'lg') else ''

    if color and color not in ('primary', 'secondary', 'dark', 'light', 'danger', 'info', 'success', 'warning'):
        color = 'primary'

    cls = f'btn {outline}{size_cls} {esc(extra_class)}'.strip()
    #     # چون تگ هست و بخواهیم به صورت رشته در بیاریم
    icon_html = ''
    if icon:
        icon_html = format_html('<i class="bi {} me-1"></i>', esc(icon))

    attrs_html = ''
    for key, value in attrs.items():
        attr_name = key.replace('_', '-')
        attrs_html += format_html(' {}="{}"', esc(attr_name), esc(value))

    modal_attrs = ''
    if modal_target:
        modal_attrs = format_html(' data-bs-toggle="modal" data-bs-target="{}"', esc(modal_target))

    if url and type == 'link':
        confirm_attr = ''
        if confirm:
            confirm_js = f'return confirm("{esc(confirm)}");'
            confirm_attr = format_html(' onclick="{}"', mark_safe(confirm_js))

        return format_html(
            '<a href="{}" class="{}"{}{}{}>{}</a>',
            esc(url), cls, confirm_attr, modal_attrs, mark_safe(attrs_html), mark_safe(icon_html + esc(label))
        )

    else:
        confirm_attr = ''
        if confirm:
            confirm_js = f'return confirm("{esc(confirm)}");'
            confirm_attr = format_html(' onclick="{}"', mark_safe(confirm_js))

        btn_type = esc(type) if type else 'submit'
        return format_html(
            '<button type="{}" class="{}"{}{}{}>{}</button>',
            btn_type, cls, confirm_attr, modal_attrs, mark_safe(attrs_html), mark_safe(icon_html + esc(label))
        )
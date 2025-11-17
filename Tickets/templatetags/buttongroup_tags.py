from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def category_button_group(categories):
    """
    Display categories as solid buttons (not outline) with 10 per row
    Usage: {% category_button_group active_categories %}
    """
    esc = conditional_escape

    if not categories:
        return format_html('<div class="alert alert-info">No categories found</div>')


    def get_category_color(category):
        ticket_count = getattr(category, 'ticket_count', 0)
        if ticket_count == 0:
            return 'btn-secondary'
        elif 1 <= ticket_count <= 5:
            return 'btn-info'
        elif 6 <= ticket_count <= 15:
            return 'btn-success'
        elif 16 <= ticket_count <= 30:
            return 'btn-warning'
        else:  # 31 and above
            return 'btn-danger'

    rows_html = ''
    current_row = ''

    for i, category in enumerate(categories):
        color_class = get_category_color(category)

        button_html = format_html(
            '<a href="Tickets?category={}" class="btn {} me-2 mb-2">{}</a>',
            esc(category.id),
            color_class,
            mark_safe(
                f'{esc(category.name)} <span class="badge bg-light text-dark ms-1">{category.ticket_count}</span>')
        )
        current_row += button_html

        if (i + 1) % 10 == 0:
            rows_html += format_html('<div class="mb-3">{}</div>', mark_safe(current_row))
            current_row = ''

    if current_row:
        rows_html += format_html('<div class="mb-3">{}</div>', mark_safe(current_row))

    return mark_safe(rows_html)
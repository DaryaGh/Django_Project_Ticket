from django import template
from django.utils.html import format_html, conditional_escape

register = template.Library()

@register.simple_tag
def widget_card_PERCENTAGE(title, count, color='primary', url=None, icon="", extra_class='',
                size='sm', btn_icon="arrow-right", btn_text="Read More",
                title_color=None, btn_color=None, extra_text=""):
    """
    نمایش ویجت کارت با امکان نمایش متن اضافی (مثل تعداد تیکت)
    """
    esc = conditional_escape

    valid_colors = ('primary', 'secondary', 'dark', 'light', 'danger', 'info', 'success', 'warning')
    if color not in valid_colors:
        color = 'primary'

    title_clr = title_color if title_color and title_color in valid_colors else 'dark'
    btn_clr = btn_color if btn_color and btn_color in valid_colors else color

    base_classes = f'card border-{esc(color)} shadow-sm h-100 d-flex flex-column {esc(extra_class)}'.strip()

    icon_html = ""
    if icon:
        icon_html = format_html(
            '''<div class="text-center mb-3">
                <div class="d-inline-flex align-items-center justify-content-center border border-{} rounded-circle bg-light" style="width: 80px; height: 80px;">
                    <i class="bi bi-{} fs-2 text-{}"></i>
                </div>
            </div>''',
            esc(color), esc(icon), esc(color)
        )

    title_html = ""
    if title:
        title_html = format_html(
            '<h5 class="card-title text-center text-{} mb-2">{}</h5>',
            esc(title_clr), esc(title)
        )

    count_html = ""
    if count is not None:
        count_html = format_html(
            '<div class="h2 fw-bold text-dark text-center mb-2">{}</div>',
            esc(count)
        )

    extra_html = ""
    if extra_text:
        extra_html = format_html(
            '<div class="text-center text-muted mb-3"><small>{}</small></div>',
            esc(extra_text)
        )

    link_html = ''
    if url is not None:
        if btn_icon:
            link_html = format_html(
                '<div class="mt-auto text-center"><a href="{}" class="btn btn-{} btn-sm"><i class="bi bi-{} me-2"></i>{}</a></div>',
                esc(url), esc(btn_clr), esc(btn_icon), esc(btn_text)
            )
        else:
            link_html = format_html(
                '<div class="mt-auto text-center"><a href="{}" class="btn btn-{} btn-sm">{}</a></div>',
                esc(url), esc(btn_clr), esc(btn_text)
            )

    return format_html(
        '''<div class="{}">
            <div class="card-body py-4 d-flex flex-column">
                {}{}{}{}{}
            </div>
        </div>''',
        base_classes,
        icon_html,
        title_html,
        count_html,
        extra_html,
        link_html
    )

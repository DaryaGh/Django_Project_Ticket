from django import template
from django.utils.safestring import mark_safe
import difflib
from django.utils.timesince import timesince

from Tickets.Choices import STATUS_COLORS

register = template.Library()

@register.filter
def format_with_highlight(old_value, new_value):
    old_text = str(old_value) if old_value not in [None, ""] else "(None)"
    new_text = str(new_value) if new_value not in [None, ""] else "(None)"

    if old_text == new_text:
        return mark_safe(f'"{new_text}" -> "{new_text}"')

    diff = difflib.SequenceMatcher(None, old_text, new_text)

    old_highlighted = []
    new_highlighted = []

    for tag, i1, i2, j1, j2 in diff.get_opcodes():
        if tag == 'equal':
            old_highlighted.append(old_text[i1:i2])
            new_highlighted.append(new_text[j1:j2])
        elif tag == 'replace':
            old_highlighted.append(f'<span class="char-removed">{old_text[i1:i2]}</span>')
            new_highlighted.append(f'<span class="char-added">{new_text[j1:j2]}</span>')
        elif tag == 'delete':
            old_highlighted.append(f'<span class="char-removed">{old_text[i1:i2]}</span>')
        elif tag == 'insert':
            new_highlighted.append(f'<span class="char-added">{new_text[j1:j2]}</span>')

    return mark_safe(f'''
    "<span>{"".join(old_highlighted)}</span>" 
    <i class="fas fa-arrow-right mx-1"></i> 
    "<span>{"".join(new_highlighted)}</span>"
    ''')

@register.filter
def time_ago(value):
    """تبدیل تاریخ به فرمت 'x دقیقه پیش'"""
    if not value:
        return ''
    return f'{timesince(value)} پیش'

@register.filter
def is_expired(ticket):
    """بررسی منقضی شدن تیکت"""
    from django.utils import timezone
    return ticket.max_replay_date < timezone.now() if ticket.max_replay_date else False


@register.filter(name='get_status_color')
def get_status_color(status):
    """فیلتر برای گرفتن رنگ وضعیت"""
    return STATUS_COLORS.get(status, '#6c757d')

@register.filter(name='format_with_highlight')
def format_with_highlight(old_value, new_value):
    """فیلتر برای نمایش تغییرات با هایلایت"""
    if not old_value or not new_value:
        return f'{old_value} → {new_value}'

    return f'"{old_value}" → "{new_value}"'

@register.filter(name='filesizeformat')
def filesizeformat(value):
    """فیلتر برای فرمت‌بندی حجم فایل"""
    try:
        value = int(value)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if value < 1024.0:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{value:.1f} TB"
    except (ValueError, TypeError):
        return "0 B"
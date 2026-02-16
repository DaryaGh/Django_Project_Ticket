from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('dashboard/priority_card.html')
def priority_card(priority_data, priority_type):
    """Template tag برای نمایش کارت priority"""
    colors = {
        'low': 'success',
        'middle': 'warning',
        'high': 'danger',
        'critical': 'danger',
        'secret': 'secondary'
    }

    icons = {
        'low': 'arrow-down-circle',
        'middle': 'dash-circle',
        'high': 'exclamation-triangle',
        'critical': 'fire',
        'secret': 'shield-lock'
    }

    return {
        'priority': priority_type,
        'count': priority_data['count'],
        'percentage': priority_data['percentage'],
        'color': colors.get(priority_type, 'secondary'),
        'icon': icons.get(priority_type, 'circle')
    }


@register.simple_tag
def calculate_percentage(count, total):
    """محاسبه درصد"""
    if total > 0:
        return round((count / total) * 100, 1)
    return 0

# در dashboard_tags.py یا یک فایل جدید
from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """تفریق دو مقدار"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value


# در dashboard_tags.py یا فایل template tags موجود
from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """تفریق دو مقدار"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """تقسیم دو مقدار"""
    try:
        arg = float(arg)
        if arg != 0:
            return float(value) / arg
        return 0
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """ضرب دو مقدار"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
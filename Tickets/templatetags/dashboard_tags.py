from django import template

register = template.Library()

@register.simple_tag
def calculate_percentage(count, total):
    """محاسبه درصد"""
    if total > 0:
        return round((count / total) * 100, 1)
    return 0

@register.filter
def subtract(value, arg):
    """تفریق دو مقدار"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

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
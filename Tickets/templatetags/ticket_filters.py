from django import template
from Tickets.Choices import STATUS_COLORS
from Tickets.models import Ticket, Assignment
#
# register = template.Library()
# @register.filter(name='get_status_color')
# def get_status_color(status):
#     """فیلتر برای گرفتن رنگ وضعیت"""
#     return STATUS_COLORS.get(status, '#6c757d')
#
# @register.filter(name='format_with_highlight')
# def format_with_highlight(old_value, new_value):
#     """فیلتر برای نمایش تغییرات با هایلایت"""
#     if not old_value or not new_value:
#         return f'{old_value} → {new_value}'
#
#     return f'"{old_value}" → "{new_value}"'
#
# @register.filter(name='filesizeformat')
# def filesizeformat(value):
#     """فیلتر برای فرمت‌بندی حجم فایل"""
#     try:
#         value = int(value)
#         for unit in ['B', 'KB', 'MB', 'GB']:
#             if value < 1024.0:
#                 return f"{value:.1f} {unit}"
#             value /= 1024.0
#         return f"{value:.1f} TB"
#     except (ValueError, TypeError):
#         return "0 B"
# در فایل templatetags/ticket-filter.py
from django import template
from django.utils.timesince import timesince

register = template.Library()


# @register.filter
# def format_with_highlight(value1, value2):
#     pass
#
# @register.filter
# def time_ago(value):
#     """تبدیل تاریخ به فرمت 'x دقیقه پیش'"""
#     if not value:
#         return ''
#     return f'{timesince(value)} پیش'
#
#
# @register.filter
# def is_expired(ticket):
#     """بررسی منقضی شدن تیکت"""
#     from django.utils import timezone
#     return ticket.max_replay_date < timezone.now() if ticket.max_replay_date else False
#

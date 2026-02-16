# from django.core.exceptions import PermissionDenied
# from django.shortcuts import redirect
# from Tickets.models import UserRole
#
#
# def super_admin_required(view_func):
#     """دکوراتور برای دسترسی فقط Super Admin"""
#
#     def wrapper(request, *args, **kwargs):
#         user_role = request.session.get('role')
#         if user_role == 'Super Admin':
#             return view_func(request, *args, **kwargs)
#         else:
#             raise PermissionDenied
#
#     return wrapper
#
#
# def check_ticket_access(view_func):
#     """دکوراتور برای بررسی دسترسی به تیکت خاص"""
#
#     def wrapper(request, *args, **kwargs):
#         from .models import Ticket
#
#         user = request.user
#         user_role = request.session.get('role', 'User')
#
#         # اگر Super Admin هست، اجازه دسترسی بده
#         if user_role == 'Super Admin':
#             return view_func(request, *args, **kwargs)
#
#         # گرفتن ticket_id از پارامترها
#         ticket_id = kwargs.get('id') or kwargs.get('ticket_id')
#
#         if ticket_id:
#             ticket = Ticket.objects.get(id=ticket_id)
#
#             # بررسی دسترسی
#             has_access = False
#
#             if user_role == "Admin":
#                 # Admin فقط تیکت‌های خودش
#                 has_access = ticket.created_by == user
#             elif user_role == "Employee":
#                 # Employee تیکت‌های خودش + تیکت‌های assigned شده
#                 has_access = (ticket.created_by == user or
#                               ticket.assignments_tickets.filter(assignee=user).exists())
#             else:
#                 # کاربر عادی فقط تیکت‌های خودش
#                 has_access = ticket.created_by == user
#
#             if not has_access:
#                 raise PermissionDenied("شما دسترسی به این تیکت را ندارید.")
#
#         return view_func(request, *args, **kwargs)
#
#     return wrapper
from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('Tickets', index, name='tickets'),
    path('Tickets/create', ticket_create, name='tickets-create'),
    path('Tickets/<int:id>/details', ticket_details, name='tickets-details'),
    path('Tickets/<int:id>/edit', ticket_update, name='tickets-update'),
    path('Tickets/delete/<int:id>', ticket_delete, name='tickets-destroy'),
    # path('Change/mode',change_mode,name='change-mode'),
    path('Tickets/success/<int:id>', ticket_success, name='ticket_success'),
    path('Tickets/search-logs/', search_logs, name='search_logs'),
    path('Tickets/Attachments/<int:id>/delete', ticket_attachment_delete, name='attachment_delete'),
    path('Tickets/Register', register, name='register'),
    path('Tickets/login', ticket_login, name='tickets-login'),
    path('Tickets/logout/', ticket_logout, name='tickets-logout'),
    path('ticket/<int:ticket_id>/attachments/delete-all/', ticket_attachments_delete_all,name='ticket-attachments-delete-all'),
    path('ticket/<int:ticket_id>/attachments/download-all/', download_all_attachments,name='ticket-attachments-download-all'),
    path('ticket/<int:id>/seen/', mark_ticket_seen, name='mark_ticket_seen'),
    path('ticket/<int:ticket_id>/seen-details/', ticket_seen_details, name='ticket_seen_details'),
]
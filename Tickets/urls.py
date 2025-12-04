from django.urls import path
from .views import *
urlpatterns = [
    path('',dashboard,name='dashboard'),
    path('Tickets',index,name='tickets'),
    path('Tickets/create',ticket_create,name='tickets-create'),
    path('Tickets/<int:id>/details',ticket_details,name='tickets-details'),
    path('Tickets/<int:id>/edit',ticket_update,name='tickets-update'),
    path('Tickets/delete/<int:id>',ticket_delete,name='tickets-destroy'),
    # path('Change/mode',change_mode,name='change-mode'),
    path('Tickets/success/<int:id>', ticket_success, name='ticket_success'),
    path('Tickets/search-logs/', search_logs, name='search_logs'),
    path('Tickets/login', ticket_login, name='tickets-login'),
# راه دوم برای ساخت logSearch
    # path('Tickets/clear' , ticket_clear , name='ticket_clear'),

    path('Tickets/Attachments/<int:id>/delete',ticket_attachment_delete,name='attachment_delete'),
 ]

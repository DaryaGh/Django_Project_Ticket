from django.urls import path
from .views import *
urlpatterns = [
    path('',dashboard,name='dashboard'),
    path('Tickets',index,name='tickets'),
    path('Tickets/create',ticket_create,name='tickets-create'),
    path('Tickets/<int:id>/details',ticket_details,name='tickets-details'),
    path('Tickets/<int:id>/edit',ticket_update,name='tickets-update'),
    path('Tickets/delete/<int:id>',ticket_delete,name='tickets-destroy'),

]
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from Tickets.forms import TicketForm
from Tickets.models import Ticket

def dashboard(request):
    return HttpResponse("Dashboard")

def index(request):
    tickets = Ticket.objects.prefetch_related('tags').all()
    print(tickets[0].tags,tickets[0].id)
    return render(request,template_name='index.html',context={'tickets':tickets})
    # return HttpResponse("Hello, world. You're at the polls index.",{
    #     'tickets': tickets
    # })

def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST) #user filled the form
        if form.is_valid():
            new_ticket = form.save(commit=False) #false Ram
            # new_ticket.created_by = request.user # todo => Use Auth
            new_ticket.created_by_id = 104
            # new_ticket.save(commit=True)
            new_ticket.save()
            form.save_m2m()
            messages.success(request, 'Your ticket has been created Successfully !!!')
            return redirect('tickets')
    else:
        #Method GET
        form = TicketForm()

    return render(request,'ticket_create.html',{'form':form})
    # return HttpResponse('ticket_create')

def ticket_details(request,id):
    return HttpResponse('ticket_details')

def ticket_update(request,id):
    ticket = get_object_or_404(Ticket, id=id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.info(request, f'Ticket #{ticket.id} has been updated Successfully !!!')
            return redirect('tickets-details',id=ticket.id)
    else:
        form = TicketForm(instance=ticket)
        # instance برای نمایش دوباره مقداری که میخواهیم ویرایش کنیم است

    return render(request,'ticket_create.html',{'form':form,'ticket':ticket})
    # return HttpResponse('ticket_update')

def ticket_delete(request,id):
    ticket_remove = get_object_or_404(Ticket, id=id)
    # print(f'Ticket:{ticket_remove}')
    ticket_remove.delete()
    messages.success(request, 'Ticket Deleted Successfully !!!')
    return redirect ('tickets')
    # return HttpResponse('ticket_delete')
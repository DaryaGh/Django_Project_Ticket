from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from Tickets.forms import TicketForm
from Tickets.models import *
from django.core.exceptions import PermissionDenied
from .Choices import *
from .validators import validate

def dashboard(request):
    return render(request, 'dashboard.html', {'dashboard': dashboard})
    # return HttpResponse("Dashboard")

def index(request):
    tickets = Ticket.objects.prefetch_related('tags').all()
    print(tickets[0].tags, tickets[0].id)
    return render(request, template_name='index.html', context={'tickets': tickets})

def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        # برای پاک کردن فیلدهای اجباری در جنگو است
        form.errors.clear()

        priority_values = ",".join([choice[0] for choice in PRIORITY_CHOICES])
        department_values = ",".join([choice[0] for choice in DEPARTMENT_CHOICES])
        # قوانین اعتبارسنجی - توجه به فیلد contact_phone
        rules = {
            "category": ["required"],
            "priority": ["required", f"in:{priority_values}"],
            "department": ["required", f"in:{department_values}"],
            "subject": ["required", "min:5", "max:200"],
            "description": ["required", "min:20", "max:2000"],
            "max_replay_date": ["required", "future_date"],
            "tags": ["min_items:1", "max_items:5"],
            "contact_email": ["required", "email"],
            "contact_name": ["required", "min:2", "max:100"],
            "contact_phone": ["phone"],  # فقط قانون phone
            "due_date": ["required", "due_date"],
        }

        errors = validate(request.POST, rules)

        # if request.FILES:
        #     file_errors = validate_files(request.FILES, {"attachments": ["max_files:5", "max_file_size:10MB"]})
        #     errors.update(file_errors)

        if errors:
            for field, error in errors.items():
                form.add_error(field, error)

        elif form.is_valid():
            new_ticket = form.save(commit=False)
            new_ticket.created_by_id = 104
            new_ticket.save()
            form.save_m2m()
            # new_ticket.created_by = request.user
            #             # new_ticket.save(commit=True)

            if 'attachments' in request.FILES:
                for file in request.FILES.getlist('attachments'):
                    TicketAttachment.objects.create(
                        ticket=new_ticket,
                        file=file,
                        uploaded_by_id=104
                    )

            messages.success(request, 'Your ticket has been created successfully!')
            return redirect('ticket_detail', ticket_id=new_ticket.id)

    else:
        form = TicketForm(initial={'priority': ''})

    return render(request, 'ticket_create.html', {
        'form': form,
        'PRIORITY_CHOICES': PRIORITY_CHOICES,
        'STATUS_CHOICES': STATUS_CHOICES,
        'PRIORITY_COLORS': PRIORITY_COLORS,
        'STATUS_COLORS': STATUS_COLORS,
    })

def ticket_details(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    all_tickets = Ticket.objects.all().order_by('-created_at')
    row_number = 0
    for i, t in enumerate(all_tickets, start=1):
        if t.id == ticket.id:
            row_number = i
            break
    return render(request, 'ticket-details.html', {'ticket': ticket, 'row_number': row_number})

def ticket_update(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.info(request, f'Ticket #{ticket.id} has been updated Successfully !!!')
            return redirect('tickets-details', id=ticket.id)
    else:
        form = TicketForm(instance=ticket)
        # instance برای نمایش دوباره مقداری که میخواهیم ویرایش کنیم است

    return render(request, 'ticket_create.html', {'form': form, 'ticket': ticket})

def ticket_delete(request, id):
    try:
        ticket = Ticket.objects.get(id=id)

        if ticket.priority.upper() == 'HIGH' or ticket.priority.lower() == 'high':
            messages.error(request, 'Cannot delete tickets with HIGH priority')
            return redirect('tickets')

        ticket.delete()
        messages.success(request, 'Ticket Deleted successfully')
        return redirect('tickets')

    except PermissionDenied:
        # اگر مدل اجازه نده
        messages.error(request, 'Cannot delete tickets with HIGH priority')
        return redirect('tickets')
    except Ticket.DoesNotExist:
        messages.error(request, 'Ticket not found')
        return redirect('tickets')

# def change_mode(request):
#     # GET
#     mode = request.GET.get('mode')
#     if mode in ['dark', 'light']:
#         response = redirect(request.META.get('HTTP_REFERER', 'tickets'))
#         response.set_cookie('theme_mode', mode, max_age=365 * 24 * 60 * 60)  # 1 year
#         return response
#
#     return redirect('tickets')


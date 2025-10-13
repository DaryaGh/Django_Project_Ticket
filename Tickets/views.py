from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from unicodedata import category

from Tickets.forms import TicketForm
from Tickets.models import *
from django.core.exceptions import PermissionDenied
from .Choices import *
from .validators import validate

def dashboard(request):
    return render(request, 'dashboard.html', {'dashboard': dashboard})
    # return HttpResponse("Dashboard")

def index(request):
    search_query = request.GET.get('q',"").strip()
    print("Search_Query : ",search_query)
    category_id = request.GET.get('category')
    priority = request.GET.get('priority')
    sort = request.GET.get('sort','created_at')
    direction = request.GET.get('direction','desc')
    # tickets = Ticket.objects.prefetch_related('tags').all()
    # print(tickets[0].tags, tickets[0].id)
    # tickets = Ticket.objects.prefetch_related('tags')
    tickets = Ticket.objects.select_related('category',"created_by").prefetch_related('tags')

    if search_query:
       tickets = tickets.filter(
            Q(subject__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tracking_code__icontains=search_query)
            | Q(category__name__icontains=search_query)
            )

    if category_id and category_id not in ["","None"]:
        tickets = tickets.filter(category_id=category_id)

    if priority and priority not in ["","None"]:
        tickets = tickets.filter(priority=priority)

    if direction == 'desc':
        tickets = tickets.order_by(f"-{sort}")
    else:
        tickets = tickets.order_by({sort})

    categories = Category.objects.filter(is_active=True )
    print("Categories : ",categories)

    priorities = Ticket._meta.get_field('priority').choices
    print("priorities : ",priorities)

    columns = [
        ('tracking_code', 'Tracking Code'),
        ('subject', 'Subject'),
        ('category__name', 'Category'),
        ('priority', 'Priority'),
        ('created_at', 'Created At'),
    ]

    context = {
        'tickets': tickets,
        'search_query': search_query,
        'categories': categories,
        'priorities': priorities,
        'selected_category': category_id if category_id not in ["","None"] else"",
        'selected_priority': priority if priority not in ["","None"] else"",
        'direction': direction,
        'sort': sort,
        'columns': columns,
    }
    return render(request, template_name='index.html', context=context)

def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        # برای پاک کردن فیلدهای اجباری در جنگو است
        form.errors.clear()

        priority_values = ",".join([choice[0] for choice in PRIORITY_CHOICES])
        department_values = ",".join([choice[0] for choice in DEPARTMENT_CHOICES])
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
            "contact_phone": ["phone"],
            "due_date": ["required", "due_date"],
        }

        errors = validate(request.POST, rules)

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
            return redirect('ticket_details', ticket_id=new_ticket.id)

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


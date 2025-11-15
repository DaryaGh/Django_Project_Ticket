from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from Tickets.forms import TicketForm
from Tickets.models import *
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from .Choices import *
from .validators import validate
from django.core.paginator import Paginator

def dashboard(request):
    return render(request, 'dashboard.html', {'dashboard': dashboard})
    # return render(request, 'dashboard-component.html', {'dashboard': dashboard})
    # return HttpResponse("Dashboard")

# راه حل خودم
# def index(request):
#     search_query = request.GET.get('q', "").strip()
#     category_id = request.GET.get('category')
#     priority = request.GET.get('priority')
#     search_mode = request.GET.get('search_mode', 'and')
#     sort = request.GET.get('sort', 'created_at')
#     direction = request.GET.get('dir', 'desc')
#     with_close = request.GET.get('with_close', None)
#
#     if search_query or category_id or priority:
#         print("📝 Logging search activity...")
#         try:
#             from Tickets.signals import create_search_log
#             create_search_log(request.user, request.GET)
#         except Exception as e:
#             print(f"⚠️ Error in search logging: {e}")
#
#     tickets = Ticket.objects if with_close == "on" else Ticket.objects.is_open()
#     tickets = tickets.select_related('category', "created_by").prefetch_related('tags')
#
#     if search_query:
#         search_q = Q(
#             Q(subject__icontains=search_query)
#             | Q(description__icontains=search_query)
#             | Q(tracking_code__icontains=search_query)
#             | Q(category__name__icontains=search_query)
#         )
#
#         filter_conditions = []
#
#         if search_query:
#             filter_conditions.append(search_q)
#
#         if category_id and category_id not in ["", "None"]:
#             if search_mode == 'or':
#                 filter_conditions.append(Q(category_id=category_id))
#             else:  # AND
#                 tickets = tickets.filter(category_id=category_id)
#
#         if priority and priority not in ["", "None"]:
#             tickets = tickets.with_priority(priority)
#
#         if filter_conditions:
#             if search_mode == 'or':
#                 combined_q = Q()
#                 for condition in filter_conditions:
#                     combined_q |= condition
#                 tickets = tickets.filter(combined_q)
#             else:
#                 tickets = tickets.filter(search_q)
#
#     else:
#         if category_id and category_id not in ["", "None"]:
#             tickets = tickets.filter(category_id=category_id)
#
#         if priority and priority not in ["", "None"]:
#             tickets = tickets.with_priority(priority)
#
#     categories = Category.objects.active()
#     priorities = Ticket._meta.get_field('priority').choices
#
#     if sort:
#         if direction == 'desc':
#             tickets = tickets.order_by('-' + sort)
#         else:
#             tickets = tickets.order_by(sort)
#
#     columns = [
#         ('row', 'Row'),
#         ('tracking_code', 'Tracking Code'),
#         ('subject', 'Subject'),
#         ('created_by', 'Created By'),
#         ('priority', 'Priority'),
#         ('category__name', 'Category'),
#         ('tags', 'Tags'),
#         ('max_replay_date', 'Max Replay Date'),
#         ('created_at', 'Created At'),
#     ]
#
#     context = {
#         'tickets': tickets,
#         'search_query': search_query,
#         'selected_category': category_id if category_id not in ["", "None"] else "",
#         'selected_priority': priority if priority not in ["", "None"] else "",
#         'search_mode': search_mode,
#         'categories': categories,
#         'priorities': priorities,
#         'with_close': with_close,
#         'direction': direction,
#         'sort': sort,
#         'columns': columns,
#     }
#
#     return render(request, template_name='index.html', context=context)

def index(request):
    search_query = request.GET.get('q', "").strip()
    category_id = request.GET.get('category',"").strip()
    priority = request.GET.get('priority',"").strip()
    search_mode = request.GET.get('search_mode', 'and')
    sort = request.GET.get('sort', 'created_at')
    direction = request.GET.get('dir', 'desc')
    with_close = request.GET.get('with_close', None)

    tickets = Ticket.objects if with_close == "on" else Ticket.objects.is_open()
    tickets = tickets.select_related('category', "created_by").prefetch_related('tags')

    is_user_search = False
    new_log = None

    if search_query or category_id or priority:
        is_user_search = True
        new_log = LogSearch()

    if search_query:
        if new_log:
            new_log.search_subject = search_query
        request.session['search_query'] = search_query
        tickets = tickets.filter(
            Q(subject__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tracking_code__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )
    elif request.session.get('search_query'):
        session_query = request.session.get('search_query')
        if session_query:
            if new_log:
                new_log.search_subject = session_query
            tickets = tickets.filter(
                Q(subject__icontains=session_query)
                | Q(description__icontains=session_query)
                | Q(tracking_code__icontains=session_query)
                | Q(category__name__icontains=session_query)
            )

    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            if new_log:
                new_log.search_category = category.name
            request.session['search_category'] = category.id
            tickets = tickets.filter(category_id=category.id)
        except Category.DoesNotExist:
            pass
    elif request.session.get('search_category'):
        session_category = request.session.get('search_category')
        if session_category:
            tickets = tickets.filter(category_id=session_category)

    if priority:
        if new_log:
            new_log.search_priority = priority
        request.session['search_priority'] = priority
        tickets = tickets.filter(priority=priority)
    elif request.session.get('search_priority'):
        session_priority = request.session.get('search_priority')
        if session_priority:
            tickets = tickets.filter(priority=session_priority)


    categories = Category.objects.active()
    priorities = Ticket._meta.get_field('priority').choices

    if sort :
        if direction == 'desc':
            sort_field = f"-{sort}"
        else:
            sort_field = sort
        tickets = tickets.order_by(sort_field)

    columns = [
        ('row', 'Row'),
        ('tracking_code', 'Tracking Code'),
        ('subject', 'Subject'),
        ('created_by', 'Created By'),
        ('priority', 'Priority'),
        ('category__name', 'Category'),
        ('tags', 'Tags'),
        ('max_replay_date', 'Max Replay Date'),
        ('created_at', 'Created At'),
    ]

    selected_category = category_id if category_id else request.session.get('search_category', "")
    selected_priority = priority if priority else request.session.get('search_priority', "")
    selected_search_query = search_query if search_query else request.session.get('search_query', "")

    context = {
        'tickets': tickets,
        'search_query': selected_search_query,
        'selected_category': str(selected_category),
        'selected_priority': selected_priority,
        'search_mode': search_mode,
        'categories': categories,
        'priorities': priorities,
        'with_close': with_close,
        'direction': direction,
        'sort': sort,
        'columns': columns,
    }

    if is_user_search and new_log:
        if request.user.is_authenticated :
            new_log.user = request.user
        new_log.save()

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
            "contact_phone": ["required","phone"],
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
            #
            # if 'attachments' in request.FILES:
            #     for file in request.FILES.getlist('attachments'):
            #         TicketAttachment.objects.create(
            #             ticket=new_ticket,
            #             file=file,
            #             uploaded_by_id=104
            #         )
            #
            # messages.success(request, 'Your ticket has been created successfully!')
            # return redirect('ticket_details', ticket_id=new_ticket.id)
            messages.success(request, 'Your Ticket was successfully !')
            return redirect('ticket_success', id=new_ticket.id)

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
    # return render(request, 'ticket-details-component.html', {'ticket': ticket, 'row_number': row_number})

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

def ticket_success(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    return render(request, 'ticket_success.html', {'ticket': ticket})

# @login_required
# def search_logs(request):
#     try:
#         # اگر کاربر لاگین کرده، لاگ‌های خودش رو ببین، در غیر این صورت همه لاگ‌ها رو نشون بده
#         if request.user.is_authenticated:
#             logs = SearchLog.objects.filter(user=request.user).select_related('category').order_by('-created_at')
#             print(f"📊 Found {logs.count()} logs for user {request.user.username}")
#         else:
#             # اگر کاربر لاگین نکرده، همه لاگ‌ها رو نشون بده
#             logs = SearchLog.objects.all().select_related('category', 'user').order_by('-created_at')
#             print(f"📊 Found {logs.count()} total logs (user not authenticated)")
#
#         paginator = Paginator(logs, 20)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#
#         context = {
#             'page_obj': page_obj,
#             'logs': page_obj.object_list,
#             'user_authenticated': request.user.is_authenticated,
#         }
#         return render(request, 'search_logs.html', context)
#
#     except Exception as e:
#         print(f"❌ Error in search_logs view: {e}")
#         return redirect('tickets')

def ticket_clear(request):
    if request.session.get('search_category'):
        del request.session['search_category']
    if request.session.get('search_query'):
        del request.session['search_query']
    if request.session.get('search_priority'):
        del request.session['search_priority']
    return redirect('tickets')
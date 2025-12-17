from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from Tickets.forms import *
from Tickets.models import *
from .Choices import *
from .validators import validate
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
# نصب دانلود زیپ
from django.http import HttpResponse,HttpResponseRedirect
import zipfile
import os
from io import BytesIO

def dashboard(request):
    total_tickets = Ticket.objects.all().count()
    # محاسبه درصدها (جلوگیری از خطای تقسیم بر صفر)
    if total_tickets > 0:
        low_percentage = (Ticket.objects.with_priority('low').count() / total_tickets) * 100
        high_percentage = (Ticket.objects.with_priority('high').count() / total_tickets) * 100
        middle_percentage = (Ticket.objects.with_priority('middle').count() / total_tickets) * 100
        secret_percentage = (Ticket.objects.with_priority('secret').count() / total_tickets) * 100
        critical_percentage = (Ticket.objects.with_priority('critical').count() / total_tickets) * 100
        expired_percentage = (Ticket.objects.is_expired().count() / total_tickets) * 100
        open_percentage = (Ticket.objects.is_open().count() / total_tickets) * 100
        close_percentage = (Ticket.objects.is_close().count() / total_tickets) * 100
        status_new_percentage = (Ticket.objects.by_status('new').count() / total_tickets) * 100
        status_in_progress_percentage = (Ticket.objects.by_status('in-progress').count() / total_tickets) * 100
        status_solved_percentage = (Ticket.objects.by_status('solved').count() / total_tickets) * 100
        status_impossible_percentage = (Ticket.objects.by_status('impossible').count() / total_tickets) * 100
    else:
        # اگر تیکتی وجود ندارد، همه درصدها صفر هستند
        low_percentage = high_percentage = middle_percentage = secret_percentage = critical_percentage = 0
        expired_percentage = open_percentage = close_percentage = 0
        status_new_percentage = status_in_progress_percentage = status_solved_percentage = status_impossible_percentage = 0

    active_categories = Category.objects.active().annotate(
        ticket_count=models.Count('tickets')
    )

    context = {
        'total_tickets': total_tickets,

        # تعدادها (برای استفاده در صورت نیاز)
        'low_tickets': Ticket.objects.with_priority('low').count(),
        'high_tickets': Ticket.objects.with_priority('high').count(),
        'middle_tickets': Ticket.objects.with_priority('middle').count(),
        'secret_tickets': Ticket.objects.with_priority('secret').count(),
        'critical_tickets': Ticket.objects.with_priority('critical').count(),
        'expired_tickets': Ticket.objects.is_expired().count(),
        'open_tickets': Ticket.objects.is_open().count(),
        'close_tickets': Ticket.objects.is_close().count(),
        'status_new_tickets': Ticket.objects.by_status('new').count(),
        'status_in_progress_tickets': Ticket.objects.by_status('in-progress').count(),
        'status_solved_tickets': Ticket.objects.by_status('solved').count(),
        'status_impossible_tickets': Ticket.objects.by_status('impossible').count(),

        #  درصد را به یک رقم اعشار گرد می‌کند
        'low_percentage': round(low_percentage, 1),
        'high_percentage': round(high_percentage, 1),
        'middle_percentage': round(middle_percentage, 1),
        'secret_percentage': round(secret_percentage, 1),
        'critical_percentage': round(critical_percentage, 1),
        'expired_percentage': round(expired_percentage, 1),
        'open_percentage': round(open_percentage, 1),
        'close_percentage': round(close_percentage, 1),
        'status_new_percentage': round(status_new_percentage, 1),
        'status_in_progress_percentage': round(status_in_progress_percentage, 1),
        'status_solved_percentage': round(status_solved_percentage, 1),
        'status_impossible_percentage': round(status_impossible_percentage, 1),

        'active_categories': active_categories,
    }

    # return render(request, 'dashboard-templatetags-btn.html', context=context)
    return render(request, 'dashboard-templatetags-btn-PERCENTAGE.html', context=context)
#     return render(request, 'dashboard-templatetags-btn.html', context=context)
#     # return render(request, 'dashboard.html', {'dashboard': dashboard})
#     # return render(request, 'dashboard-component.html', {'dashboard': dashboard})
#     # return HttpResponse("Dashboard")

# @login_required(login_url='login')
def index(request):
    # اگر پارامتر clear وجود داشت، session را پاک کن
    if request.GET.get('clear'):
        if 'search_params' in request.session:
            del request.session['search_params']
        return redirect('tickets')

    # دریافت پارامترها از GET یا session
    if request.GET:
        search_params = {
            'q': request.GET.get('q', "").strip(),
            'category': request.GET.get('category'),
            'priority': request.GET.get('priority'),
            'status': request.GET.get('status'),
            'department': request.GET.get('department'),
            'response_status': request.GET.get('response_status'),  # جدید - وضعیت پاسخ
            'search_mode': request.GET.get('search_mode', 'and'),
            'sort': request.GET.get('sort', 'created_at'),
            'direction': request.GET.get('dir', 'desc'),
            'with_close': request.GET.get('with_close'),
            'created_at_from': request.GET.get('created_at_from'),
            'created_at_to': request.GET.get('created_at_to'),
            'max_replay_date_from': request.GET.get('max_replay_date_from'),
            'max_replay_date_to': request.GET.get('max_replay_date_to'),
        }
        request.session['search_params'] = search_params
    else:
        search_params = request.session.get('search_params', {})

    search_query = search_params.get('q', "")
    category_id = search_params.get('category')
    priority = search_params.get('priority')
    status = search_params.get('status')
    department = search_params.get('department')
    response_status = search_params.get('response_status')  # جدید
    search_mode = search_params.get('search_mode', 'and')
    sort = search_params.get('sort', 'created_at')
    direction = search_params.get('dir', 'desc')
    with_close = search_params.get('with_close')
    created_at_from = search_params.get('created_at_from')
    created_at_to = search_params.get('created_at_to')
    max_replay_date_from = search_params.get('max_replay_date_from')
    max_replay_date_to = search_params.get('max_replay_date_to')

    # if search_query or category_id or priority or status or department or response_status or created_at_from or created_at_to or max_replay_date_from or max_replay_date_to:
    #     try:
    #         from Tickets.signals import create_search_log
    #         create_search_log(request.user, search_params)
    #     except Exception as e:
    #         print(f" Error in search logging: {e}")

    if search_query or category_id or priority or status or department or response_status or created_at_from or created_at_to or max_replay_date_from or max_replay_date_to:
        try:
            from Tickets.signals import create_search_log
            create_search_log(request.user, {
                'q': search_query,
                'category': category_id,
                'priority': priority,
                'status': status,
                'department': department,
                'response_status': response_status,
                'search_mode': search_mode,
                'created_at_from': created_at_from,
                'created_at_to': created_at_to,
                'max_replay_date_from': max_replay_date_from,
                'max_replay_date_to': max_replay_date_to,
                'with_close': with_close,
            })
        except Exception as e:
            print(f" Error in search logging: {e}")

    # فیلتر کردن تیکت‌ها
    tickets = Ticket.objects if with_close == "on" else Ticket.objects.is_open()
    tickets = tickets.select_related('category', "created_by").prefetch_related(
        'tags',
        'responses',
        'assignments_tickets__assignee'
    )

    filter_conditions = []

    #  شرط جستجو
    if search_query:
        search_q = Q(
            Q(subject__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tracking_code__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )
        filter_conditions.append(search_q)

    #  شرط دسته‌بندی
    if category_id and category_id not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(category_id=category_id))
        else:  # AND
            tickets = tickets.filter(category_id=category_id)

    #  شرط اولویت
    if priority and priority not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(priority=priority))
        else:  # AND
            tickets = tickets.with_priority(priority)

    #  شرط وضعیت تیکت
    if status and status not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(status=status))
        else:  # AND
            tickets = tickets.by_status(status)

    #  شرط دپارتمان
    if department and department not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(department=department))
        else:
            tickets = tickets.filter(department=department)

    # ا شرط وضعیت پاسخ
    if response_status and response_status not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(responses__response_status=response_status))
        else:
            tickets = tickets.filter(responses__response_status=response_status)

    #  تاریخ ایجاد تیکت
    if created_at_from:
        if search_mode == 'or':
            filter_conditions.append(Q(created_at__date__gte=created_at_from))
        else:
            tickets = tickets.filter(created_at__date__gte=created_at_from)

    if created_at_to:
        if search_mode == 'or':
            filter_conditions.append(Q(created_at__date__lte=created_at_to))
        else:
            tickets = tickets.filter(created_at__date__lte=created_at_to)

    #  تاریخ مهلت پاسخ
    if max_replay_date_from:
        if search_mode == 'or':
            filter_conditions.append(Q(max_replay_date__date__gte=max_replay_date_from))
        else:
            tickets = tickets.filter(max_replay_date__date__gte=max_replay_date_from)

    if max_replay_date_to:
        if search_mode == 'or':
            filter_conditions.append(Q(max_replay_date__date__lte=max_replay_date_to))
        else:
            tickets = tickets.filter(max_replay_date__date__lte=max_replay_date_to)

    # اعمال فیلترها بر اساس حالت جستجو
    if filter_conditions:
        if search_mode == 'or':
            combined_q = Q()
            for condition in filter_conditions:
                combined_q |= condition
            tickets = tickets.filter(combined_q).distinct()
        else:
            # حالت AND: فقط شرط جستجو اعمال می‌شود (بقیه قبلاً اعمال شده‌اند)
            if search_query:
                tickets = tickets.filter(search_q)

    # اگر حالت AND است و هیچ جستجویی نیست، اما فیلترهای دیگر وجود دارند
    elif search_mode == 'and' and not search_query and (
            category_id or priority or status or department or response_status or created_at_from or created_at_to or max_replay_date_from or max_replay_date_to):
        # در حالت AND بدون جستجو، فیلترها قبلاً اعمال شده‌اند
        pass

    categories = Category.objects.active()
    priorities = Ticket._meta.get_field('priority').choices
    statuses = Ticket._meta.get_field('status').choices
    departments = Ticket._meta.get_field('department').choices

    # choices برای وضعیت پاسخ - جدید
    response_statuses = [
        ('sent', 'Sent'),
        ('seen', 'Seen'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]

    if sort:
        if direction == 'desc':
            tickets = tickets.order_by('-' + sort)
        else:
            tickets = tickets.order_by(sort)

    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    swipers = Swiper.objects.filter(is_active=True).order_by('-created_at')

    # برای دیباگ
    print(f"Found {swipers.count()} active swipers")
    for swiper in swipers:
        print(f"Swiper: {swiper.title}, Image: {swiper.main_image}")
        if swiper.main_image:
            print(f"Image URL: {swiper.main_image.url}")

    columns = [
        ('row', 'Row'),
        ('tracking_code', 'Tracking Code'),
        ('subject', 'Subject'),
        ('created_by', 'Created By'),
        ('priority', 'Priority'),
        ('category__name', 'Category'),
        ('tags', 'Tags'),
        ('assignees', 'Assignees'),  # ستون جدید
        ('max_replay_date', 'Max Replay Date'),
        ('created_at', 'Created At'),
        # ('status', 'Status'),  # اضافه شده
    ]

    print(f"Total tickets: {page_obj.object_list.count()}")
    for i, ticket in enumerate(page_obj.object_list, 1):
        assignee_count = ticket.assignments_tickets.count()
        print(f"Ticket {i}: {ticket.tracking_code} - Assignees: {assignee_count}")
        if assignee_count > 0:
            for assignment in ticket.assignments_tickets.all():
                print(f"  - {assignment.assignee.username}")


    context = {
        'page_obj': page_obj,
        'tickets': tickets,
        'search_query': search_query,
        'selected_category': category_id if category_id not in ["", "None"] else "",
        'selected_priority': priority if priority not in ["", "None"] else "",
        'selected_status': status if status not in ["", "None"] else "",
        'selected_department': department if department not in ["", "None"] else "",
        'selected_response_status': response_status if response_status not in ["", "None"] else "",  # جدید
        'search_mode': search_mode,
        'categories': categories,
        'priorities': priorities,
        'statuses': statuses,
        'departments': departments,
        'response_statuses': response_statuses,  # جدید
        'with_close': with_close,
        'direction': direction,
        'sort': sort,
        'columns': columns,
        'created_at_from': created_at_from,
        'created_at_to': created_at_to,
        'max_replay_date_from': max_replay_date_from,
        'max_replay_date_to': max_replay_date_to,
        'has_active_filters': bool(
            search_query or category_id or priority or status or department or response_status or created_at_from or created_at_to or max_replay_date_from or max_replay_date_to),
        'swipers': swipers,
        # 'total_tickets': Ticket.objects.count(),
    }

    # return render(request, template_name='index.html', context=context)
    # return render(request, template_name='index-card.html', context=context)
    return render(request, template_name='index-table-card.html', context=context)

def ticket_create(request):
    if not request.user.is_authenticated:  #  چک کردن لاگین بودن کاربر
        messages.error(request, 'You must be logged in to create a ticket.')
        return redirect('tickets-login')

    if request.method == 'POST':
        # form = TicketForm(request.POST)
        form = TicketForm(request.POST, request.FILES)
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
            "users":["required","min_items:1", "max_items:5"],
            "contact_email": ["required", "email"],
            "contact_name": ["required", "min:2", "max:100"],
            "contact_phone": ["required", "phone"],
            "due_date": ["required", "future_date"],
            "attachments": [
                "required",
                "file_type:application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/jpeg,image/png",
                "max_size:5", "max_files:10"]
        }

        # errors = validate(request.POST, rules)
        errors = validate(request.POST, request.FILES, rules)

        if errors:
            for field, error in errors.items():
                form.add_error(field, error)

        elif form.is_valid():
            new_ticket = form.save(commit=False)
            # new_ticket.created_by_id = 104
            new_ticket.created_by_id = request.user.id
            new_ticket.save()


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

            files = request.FILES.getlist("attachments")
            for file in files:
                TicketAttachment.objects.create(ticket=new_ticket, file=file,uploaded_by_id=request.user.id)

            form.save_m2m()

            selected_users = form.cleaned_data['users']
            assignments = []
            for user in selected_users:
                assignments.append(
                    Assignment(
                        assigned_ticket=new_ticket,
                        assignee=user,
                        status='new',
                        assigned_by_id=request.user.id
                    )
                )
            Assignment.objects.bulk_create(assignments)


            messages.success(request, 'Your ticket has been created successfully!')
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


    # return render(request, 'ticket_create-class.html', {
    #     'form': form,
    #     'PRIORITY_CHOICES': PRIORITY_CHOICES,
    #     'STATUS_CHOICES': STATUS_CHOICES,
    #     'PRIORITY_COLORS': PRIORITY_COLORS,
    #     'STATUS_COLORS': STATUS_COLORS,
    # })

def ticket_details(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    all_tickets = Ticket.objects.all().order_by('-created_at')
    row_number = 0
    for i, t in enumerate(all_tickets, start=1):
        if t.id == ticket.id:
            row_number = i
            break
    ticket = get_object_or_404(
        Ticket.objects.select_related('category', 'created_by').prefetch_related('tags', 'ticket_attachments'), id=id)

    attachments = ticket.ticket_attachments.all()
    print(ticket.ticket_attachments.all())
    return render(request, 'ticket-details.html', {
        'ticket': ticket,
        'attachments': attachments,
        'row_number': row_number
    })
    # return render(request, 'ticket-details-component.html', {'ticket': ticket, 'row_number': row_number})

def ticket_update(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()

            files = request.FILES.getlist("attachments")
            for file in files:
                TicketAttachment.objects.create(ticket=ticket, file=file)

            selected_users = set(form.cleaned_data['users'])
            # current_users = set(
            #     Ticket.assignments.value_list('assignee_id',flat=True)
            # )

            current_users = set(
                ticket.assignments_tickets.values_list('assignee_id', flat=True)  # استفاده از related_name صحیح
            )

            # Assignment.objects.filter(
            #     assignee_ticket=ticket,
            #     assignee_id__in=(current_users-set(u.id for u in selected_users)),
            # ).delete()

            # این بخش هم باید اصلاح شود - اسم فیلد اشتباه است
            Assignment.objects.filter(
                assigned_ticket=ticket,  # اصلاح: assignee_ticket به assigned_ticket
                assignee_id__in=(current_users - set(u.id for u in selected_users)),
            ).delete()

            new_assignments = [Assignment(assigned_ticket=ticket, assignee=user)
                               for user in selected_users
                               if user.id not in current_users
                               ]
            Assignment.objects.bulk_create(new_assignments)

            messages.info(request, f'Ticket #{ticket.id} has been updated Successfully !!!')
            return redirect('tickets-details', id=ticket.id)
    else:
        form = TicketForm(instance=ticket)
        # instance برای نمایش دوباره مقداری که میخواهیم ویرایش کنیم است

    return render(request, 'ticket_create.html', {
        'form': form,
        'ticket': ticket,
        'attachments': ticket.ticket_attachments.all(),
    })

def ticket_delete(request, id):
    try:
        ticket = Ticket.objects.get(id=id)

        if ticket.priority.upper() == 'HIGH' or ticket.priority.lower() == 'high':
            messages.error(request, 'Cannot delete tickets with HIGH priority')
            return redirect('tickets')

        attachments = TicketAttachment.objects.filter(ticket=ticket)
        for attachment in attachments:
            attachment.file.delete(save=False)
            attachment.delete()

        ticket.delete()
        messages.success(request, 'Ticket Deleted successfully')
        return redirect('tickets')

    except Ticket.DoesNotExist:
        messages.error(request, 'Ticket not found')
        return redirect('tickets')

def ticket_success(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    return render(request, 'ticket_success.html', {'ticket': ticket})

# @login_required
def search_logs(request):
    try:
        # اگر کاربر لاگین کرده، لاگ‌های خودش رو ببین، در غیر این صورت همه لاگ‌ها رو نشون بده
        if request.user.is_authenticated:
            logs = SearchLogSignal.objects.filter(user=request.user).select_related('category').order_by('-created_at')
            print(f" Found {logs.count()} logs for user {request.user.username}")
        else:
            # اگر کاربر لاگین نکرده، همه لاگ‌ها رو نشون بده
            logs = SearchLogSignal.objects.all().select_related('category', 'user').order_by('-created_at')
            print(f" Found {logs.count()} total logs (user not authenticated)")

        paginator = Paginator(logs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'logs': page_obj.object_list,
            'user_authenticated': request.user.is_authenticated,
        }
        return render(request, 'search_logs.html', context)

    except Exception as e:
        print(f" Error in search_logs view: {e}")
        return redirect('tickets')

def ticket_login(request):
    swipers = Swiper.objects.filter(is_active=True).order_by('-created_at')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login-page.html', {'swipers': swipers})

def ticket_attachment_delete(request, id):
    attachment = get_object_or_404(TicketAttachment, id=id)
    ticket = attachment.ticket

    attachment.file.delete(save=False)
    attachment.delete()

    messages.success(request, 'Ticket Attachment Deleted Successfully')
    return redirect('tickets-update', id=ticket.id)

def ticket_attachments_delete_all(request, ticket_id):
    """حذف تمام attachment های یک تیکت"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        attachments = ticket.ticket_attachments.all()
        count = attachments.count()

        # حذف تمام فایل‌ها
        for attachment in attachments:
            attachment.file.delete(save=False)
            attachment.delete()

        messages.success(request, f'{count} attachment(s) deleted successfully')
        return redirect('tickets-update', id=ticket.id)

    # اگر درخواست GET بود به صفحه جزئیات برگرد
    return redirect('tickets-details', id=ticket.id)

def download_all_attachments(request, ticket_id):
    """دانلود تمام attachment های یک تیکت به صورت ZIP"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    attachments = ticket.ticket_attachments.all()

    if not attachments.exists():
        messages.warning(request, 'No attachments found')
        return redirect('tickets-details', id=ticket.id)

    # ایجاد بافر برای ZIP
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for attachment in attachments:
            try:
                # خواندن فایل از storage
                with attachment.file.open('rb') as f:
                    # نام فایل را استخراج کن (بدون مسیر کامل)
                    filename = os.path.basename(attachment.file.name)
                    zip_file.writestr(filename, f.read())
            except Exception as e:
                # در صورت خطا ادامه بده و فایل بعدی را اضافه کن
                continue

    # تنظیم response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}_attachments.zip"'
    response['Content-Length'] = buffer.tell()

    return response

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account was created successfully . Please login to continue')
            return redirect('tickets-login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def ticket_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('tickets-login')

# ---------------------------------------------------------------------------------------------
# راه دوم برای ساخت logSearch
# def index(request):
#     search_query = request.GET.get('q', "").strip()
#     category_id = request.GET.get('category',"").strip()
#     priority = request.GET.get('priority',"").strip()
#     search_mode = request.GET.get('search_mode', 'and')
#     sort = request.GET.get('sort', 'created_at')
#     direction = request.GET.get('dir', 'desc')
#     with_close = request.GET.get('with_close', None)
#
#     tickets = Ticket.objects if with_close == "on" else Ticket.objects.is_open()
#     tickets = tickets.select_related('category', "created_by").prefetch_related('tags')
#
#     is_user_search = False
#     new_log = None
#
#     if search_query or category_id or priority:
#         is_user_search = True
#         new_log = LogSearch()
#
#     if search_query:
#         if new_log:
#             new_log.search_subject = search_query
#         request.session['search_query'] = search_query
#         tickets = tickets.filter(
#             Q(subject__icontains=search_query)
#             | Q(description__icontains=search_query)
#             | Q(tracking_code__icontains=search_query)
#             | Q(category__name__icontains=search_query)
#         )
#     elif request.session.get('search_query'):
#         session_query = request.session.get('search_query')
#         if session_query:
#             if new_log:
#                 new_log.search_subject = session_query
#             tickets = tickets.filter(
#                 Q(subject__icontains=session_query)
#                 | Q(description__icontains=session_query)
#                 | Q(tracking_code__icontains=session_query)
#                 | Q(category__name__icontains=session_query)
#             )
#
#     if category_id:
#         try:
#             category = Category.objects.get(id=category_id)
#             if new_log:
#                 new_log.search_category = category.name
#             request.session['search_category'] = category.id
#             tickets = tickets.filter(category_id=category.id)
#         except Category.DoesNotExist:
#             pass
#     elif request.session.get('search_category'):
#         session_category = request.session.get('search_category')
#         if session_category:
#             tickets = tickets.filter(category_id=session_category)
#
#     if priority:
#         if new_log:
#             new_log.search_priority = priority
#         request.session['search_priority'] = priority
#         tickets = tickets.filter(priority=priority)
#     elif request.session.get('search_priority'):
#         session_priority = request.session.get('search_priority')
#         if session_priority:
#             tickets = tickets.filter(priority=session_priority)
#
#
#     categories = Category.objects.active()
#     priorities = Ticket._meta.get_field('priority').choices
#
#     if sort :
#         if direction == 'desc':
#             sort_field = f"-{sort}"
#         else:
#             sort_field = sort
#         tickets = tickets.order_by(sort_field)
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
#     selected_category = category_id if category_id else request.session.get('search_category', "")
#     selected_priority = priority if priority else request.session.get('search_priority', "")
#     selected_search_query = search_query if search_query else request.session.get('search_query', "")
#
#     context = {
#         'tickets': tickets,
#         'search_query': selected_search_query,
#         'selected_category': str(selected_category),
#         'selected_priority': selected_priority,
#         'search_mode': search_mode,
#         'categories': categories,
#         'priorities': priorities,
#         'with_close': with_close,
#         'direction': direction,
#         'sort': sort,
#         'columns': columns,
#     }
#
#     if is_user_search and new_log:
#         if request.user.is_authenticated :
#             new_log.user = request.user
#         new_log.save()
#
#     return render(request, template_name='index.html', context=context)
# def ticket_clear(request):
#     if request.session.get('search_category'):
#         del request.session['search_category']
#     if request.session.get('search_query'):
#         del request.session['search_query']
#     if request.session.get('search_priority'):
#         del request.session['search_priority']
#     return redirect('tickets')
# def ticket_login(request):
#     swipers = Swiper.objects.filter(is_active=True).order_by('-created_at')
#     return render(request, 'registration/login-page.html', {'swipers': swipers})

# def dashboard(request):
# تعداد تیکت ها
#     # active_categories = Category.objects.active()
#     active_categories = Category.objects.active().annotate(
#         ticket_count=models.Count('tickets')
#     )
#
#     context = {
#         'total_tickets': Ticket.objects.all().count(),
#         'low_tickets': Ticket.objects.with_priority('low').count(),
#         'high_tickets': Ticket.objects.with_priority('high').count(),
#         'middle_tickets': Ticket.objects.with_priority('middle').count(),
#         'secret_tickets': Ticket.objects.with_priority('secret').count(),
#         'critical_tickets': Ticket.objects.with_priority('critical').count(),
#         'expired_tickets': Ticket.objects.is_expired().count(),
#         'open_tickets': Ticket.objects.is_open().count(),
#         'close_tickets': Ticket.objects.is_close().count(),
#         'status_new_tickets': Ticket.objects.by_status('new').count(),
#         'status_in_progress_tickets': Ticket.objects.by_status('in-progress').count(),
#         'status_solved_tickets': Ticket.objects.by_status('solved').count(),
#         'status_impossible_tickets': Ticket.objects.by_status('impossible').count(),
#         # 'tags': Ticket.objects.with_tags().count(),
#         # 'assigned_by_author_user':Ticket.objects.assigned_by(request.user).count(),
#         'active_categories': active_categories,
#     }
#     # return render(request, 'dashboard-templatetags.html', context=context)
#     return render(request, 'dashboard-templatetags-btn.html', context=context)
#     # return render(request, 'dashboard.html', {'dashboard': dashboard})
#     # return render(request, 'dashboard-component.html', {'dashboard': dashboard})
#     # return HttpResponse("Dashboard")
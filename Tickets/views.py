from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timesince import timesince
from django.utils.translation import activate
from pip._internal.utils._jaraco_text import _

from Tickets.forms import *
from Tickets.models import *
from Tickets.services import *
from .Choices import *
from .validators import validate
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
# نصب دانلود زیپ
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
import zipfile
import os
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
# برای 403
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json


@login_required()
def dashboard(request):
    user = request.user
    # دریافت نقش کاربر از Group
    if user.is_superuser:
        role_title = "Super Admin"
    else:
        group = user.groups.first()
        role_title = group.name if group else "User"

    request.session['role'] = role_title


    if role_title == "Super Admin":
        base_queryset = Ticket.objects.all()
        assignments_base = Assignment.objects.all()
        all_groups = Group.objects.all()
    else:
        #  **برای همه کاربران غیر Super Admin: فقط تیکت‌های ایجاد شده توسط خودشان**
        base_queryset = Ticket.objects.filter(created_by=request.user)
        assignments_base = Assignment.objects.filter(
            Q(assignee=request.user) |
            Q(assigned_by=request.user)
        ).distinct()
        all_groups = Group.objects.filter(user=request.user)


    total_tickets = base_queryset.count()
    seen_tickets = base_queryset.filter(seen_at__isnull=False).count()
    unseen_tickets = total_tickets - seen_tickets


    if total_tickets > 0:
        low_percentage = (base_queryset.with_priority('low').count() / total_tickets) * 100
        high_percentage = (base_queryset.with_priority('high').count() / total_tickets) * 100
        middle_percentage = (base_queryset.with_priority('middle').count() / total_tickets) * 100
        secret_percentage = (base_queryset.with_priority('secret').count() / total_tickets) * 100
        critical_percentage = (base_queryset.with_priority('critical').count() / total_tickets) * 100
        expired_percentage = (base_queryset.is_expired().count() / total_tickets) * 100
        open_percentage = (base_queryset.is_open().count() / total_tickets) * 100
        close_percentage = (base_queryset.is_close().count() / total_tickets) * 100
        status_new_percentage = (base_queryset.by_status('new').count() / total_tickets) * 100
        status_in_progress_percentage = (base_queryset.by_status('in-progress').count() / total_tickets) * 100
        status_solved_percentage = (base_queryset.by_status('solved').count() / total_tickets) * 100
        status_impossible_percentage = (base_queryset.by_status('impossible').count() / total_tickets) * 100
        seen_percentage = (seen_tickets / total_tickets) * 100
        unseen_percentage = 100 - seen_percentage
    else:
        # اگر تیکتی وجود ندارد، همه درصدها صفر هستند
        low_percentage = high_percentage = middle_percentage = secret_percentage = critical_percentage = 0
        expired_percentage = open_percentage = close_percentage = 0
        status_new_percentage = status_in_progress_percentage = status_solved_percentage = status_impossible_percentage = 0
        seen_percentage = 0
        unseen_percentage = 0

    low_tickets = base_queryset.with_priority('low').count()
    high_tickets = base_queryset.with_priority('high').count()
    middle_tickets = base_queryset.with_priority('middle').count()
    secret_tickets = base_queryset.with_priority('secret').count()
    critical_tickets = base_queryset.with_priority('critical').count()
    expired_tickets = base_queryset.is_expired().count()
    open_tickets = base_queryset.is_open().count()
    close_tickets = base_queryset.is_close().count()
    status_new_tickets = base_queryset.by_status('new').count()
    status_in_progress_tickets = base_queryset.by_status('in-progress').count()
    status_solved_tickets = base_queryset.by_status('solved').count()
    status_impossible_tickets = base_queryset.by_status('impossible').count()


    if role_title == "Super Admin":
        user_categories = Category.objects.filter(
            tickets__isnull=False
        ).distinct().count()
        categories_with_tickets = Category.objects.filter(
            tickets__isnull=False
        ).distinct().count()
    else:
        user_categories = Category.objects.filter(
            tickets__created_by=request.user
        ).distinct().count()
        categories_with_tickets = Category.objects.filter(
            tickets__isnull=False
        ).distinct().count()


    if role_title == "Super Admin":
        user_category_list = Category.objects.filter(
            tickets__isnull=False
        ).distinct().annotate(
            ticket_count=models.Count('tickets')
        )
    else:
        user_category_list = Category.objects.filter(
            tickets__created_by=request.user
        ).distinct().annotate(
            ticket_count=models.Count('tickets', filter=models.Q(tickets__created_by=request.user))
        )


    sent_tasks = assignments_base.filter(assigned_by=request.user).count()
    received_tasks = assignments_base.filter(assignee=request.user).count()

    if role_title == "Super Admin":
        total_tasks = assignments_base.count()
    else:
        total_tasks = sent_tasks + received_tasks

    open_sent_tasks = assignments_base.filter(
        assigned_by=request.user,
        status__in=['new', 'in-progress']
    ).count() if assignments_base.exists() else 0

    open_received_tasks = assignments_base.filter(
        assignee=request.user,
        status__in=['new', 'in-progress']
    ).count() if assignments_base.exists() else 0

    closed_sent_tasks = assignments_base.filter(
        assigned_by=request.user,
        status__in=['solved', 'closed']
    ).count() if assignments_base.exists() else 0

    closed_received_tasks = assignments_base.filter(
        assignee=request.user,
        status__in=['solved', 'closed']
    ).count() if assignments_base.exists() else 0


    if total_tasks > 0:
        sent_tasks_percentage = round((sent_tasks / total_tasks) * 100, 1)
        received_tasks_percentage = round((received_tasks / total_tasks) * 100, 1)
        open_tasks_percentage = round(((open_sent_tasks + open_received_tasks) / total_tasks) * 100, 1)
    else:
        sent_tasks_percentage = received_tasks_percentage = open_tasks_percentage = 0


    group_statistics = []

    if role_title == "Super Admin":
        for group in all_groups:
            users_in_group = User.objects.filter(groups=group)
            group_tickets = Ticket.objects.filter(created_by__in=users_in_group)

            group_stats = {
                'group': group,
                'user_count': users_in_group.count(),
                'total_tickets': group_tickets.count(),
                'open_tickets': group_tickets.filter(closed_at__isnull=True).count(),
                'closed_tickets': group_tickets.filter(closed_at__isnull=False).count(),
                'seen_tickets': group_tickets.filter(seen_at__isnull=False).count(),
                'sent_tasks': Assignment.objects.filter(assigned_by__in=users_in_group).count(),
                'received_tasks': Assignment.objects.filter(assignee__in=users_in_group).count(),
                'tickets_by_priority': {
                    'low': group_tickets.filter(priority='low').count(),
                    'middle': group_tickets.filter(priority='middle').count(),
                    'high': group_tickets.filter(priority='high').count(),
                    'critical': group_tickets.filter(priority='critical').count(),
                    'secret': group_tickets.filter(priority='secret').count(),
                },
                'tickets_by_status': {
                    'new': group_tickets.filter(status='new').count(),
                    'in_progress': group_tickets.filter(status='in_progress').count(),
                    'solved': group_tickets.filter(status='solved').count(),
                    'impossible': group_tickets.filter(status='impossible').count(),
                }
            }

            if group_stats['total_tickets'] > 0:
                group_stats['open_percentage'] = round(
                    (group_stats['open_tickets'] / group_stats['total_tickets']) * 100, 1)
                group_stats['seen_percentage'] = round(
                    (group_stats['seen_tickets'] / group_stats['total_tickets']) * 100, 1)
            else:
                group_stats['open_percentage'] = 0
                group_stats['seen_percentage'] = 0

            group_statistics.append(group_stats)
    else:

        for group in all_groups:

            users_in_group = User.objects.filter(groups=group)
            group_tickets = base_queryset.filter(created_by__in=users_in_group)

            group_stats = {
                'group': group,
                'user_count': 1,
                'total_tickets': group_tickets.count(),
                'open_tickets': group_tickets.filter(closed_at__isnull=True).count(),
                'closed_tickets': group_tickets.filter(closed_at__isnull=False).count(),
                'seen_tickets': group_tickets.filter(seen_at__isnull=False).count(),
                'sent_tasks': assignments_base.filter(assigned_by=request.user).count(),
                'received_tasks': assignments_base.filter(assignee=request.user).count(),
                'tickets_by_priority': {
                    'low': group_tickets.filter(priority='low').count(),
                    'middle': group_tickets.filter(priority='middle').count(),
                    'high': group_tickets.filter(priority='high').count(),
                    'critical': group_tickets.filter(priority='critical').count(),
                    'secret': group_tickets.filter(priority='secret').count(),
                },
                'tickets_by_status': {
                    'new': group_tickets.filter(status='new').count(),
                    'in-progress': group_tickets.filter(status='in-progress').count(),
                    'solved': group_tickets.filter(status='solved').count(),
                    'impossible': group_tickets.filter(status='impossible').count(),
                }
            }

            if group_stats['total_tickets'] > 0:
                group_stats['open_percentage'] = round(
                    (group_stats['open_tickets'] / group_stats['total_tickets']) * 100, 1)
                group_stats['seen_percentage'] = round(
                    (group_stats['seen_tickets'] / group_stats['total_tickets']) * 100, 1)
            else:
                group_stats['open_percentage'] = 0
                group_stats['seen_percentage'] = 0

            group_statistics.append(group_stats)

    context = {
        "page_title": " Dashboard | Ticketing",
        'total_tickets': total_tickets,
        'seen_tickets': seen_tickets,
        'unseen_tickets': unseen_tickets,
        'seen_percentage': round(seen_percentage, 1),
        'unseen_percentage': round(unseen_percentage, 1),
        'low_tickets': low_tickets,
        'high_tickets': high_tickets,
        'middle_tickets': middle_tickets,
        'secret_tickets': secret_tickets,
        'critical_tickets': critical_tickets,
        'expired_tickets': expired_tickets,
        'open_tickets': open_tickets,
        'close_tickets': close_tickets,
        'status_new_tickets': status_new_tickets,
        'status_in_progress_tickets': status_in_progress_tickets,
        'status_solved_tickets': status_solved_tickets,
        'status_impossible_tickets': status_impossible_tickets,
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
        'user_categories_count': user_categories,
        'categories_with_tickets': categories_with_tickets,
        'user_category_list': user_category_list,
        'total_tasks': total_tasks,
        'sent_tasks': sent_tasks,
        'received_tasks': received_tasks,
        'open_sent_tasks': open_sent_tasks,
        'open_received_tasks': open_received_tasks,
        'closed_sent_tasks': closed_sent_tasks,
        'closed_received_tasks': closed_received_tasks,
        'sent_tasks_percentage': sent_tasks_percentage,
        'received_tasks_percentage': received_tasks_percentage,
        'open_tasks_percentage': open_tasks_percentage,
        'group_statistics': group_statistics,
        'user_role': role_title,
        'is_super_admin': role_title == "Super Admin",
    }

    return render(request, 'dashboard-templatetags-btn-PERCENTAGE-seen.html', context)

@login_required()
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
            'response_status': request.GET.get('response_status'),
            'search_mode': request.GET.get('search_mode', 'and'),
            'sort': request.GET.get('sort', 'created_at'),
            'direction': request.GET.get('dir', 'desc'),
            'with_close': request.GET.get('with_close', 'off'),
            'created_at_from': request.GET.get('created_at_from'),
            'created_at_to': request.GET.get('created_at_to'),
            'max_replay_date_from': request.GET.get('max_replay_date_from'),
            'max_replay_date_to': request.GET.get('max_replay_date_to'),
            'seen': request.GET.get('seen'),
        }
        request.session['search_params'] = search_params
    else:
        search_params = request.session.get('search_params', {})
    search_query = search_params.get('q', "")
    category_id = search_params.get('category')
    priority = search_params.get('priority')
    status = search_params.get('status')
    department = search_params.get('department')
    response_status = search_params.get('response_status')
    search_mode = search_params.get('search_mode', 'and')
    sort = search_params.get('sort', 'created_at')
    direction = search_params.get('dir', 'desc')
    with_close = search_params.get('with_close', 'off')
    created_at_from = search_params.get('created_at_from')
    created_at_to = search_params.get('created_at_to')
    max_replay_date_from = search_params.get('max_replay_date_from')
    max_replay_date_to = search_params.get('max_replay_date_to')
    seen = search_params.get('seen')

    if search_query or category_id or priority or status or department or response_status or created_at_from or created_at_to or max_replay_date_from or max_replay_date_to or seen:
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
                'seen': seen,
            })
        except Exception as e:
            print(f" Error in search logging: {e}")


    user_role = request.session.get("role", "User")


    if user_role == "Super Admin":
        base_queryset = Ticket.objects.all()
        print(f"INDEX: 👑 SUPER ADMIN sees ALL tickets")
    elif user_role == "Admin":

        base_queryset = Ticket.objects.filter(created_by=request.user)
        print(f"INDEX: 🔧 ADMIN sees ONLY OWN created tickets")
    elif user_role == "Employee":

        base_queryset = Ticket.objects.filter(created_by=request.user)
        print(f"INDEX: 👨‍💼 EMPLOYEE sees ONLY OWN created tickets")
    else:
        base_queryset = Ticket.objects.filter(created_by=request.user)
        print(f"INDEX: 👤 USER sees only OWN created tickets")


    if with_close != 'on':
        base_queryset = base_queryset.filter(closed_at__isnull=True)

    filter_conditions = []

    if search_query:
        search_q = Q(
            Q(subject__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tracking_code__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )
        filter_conditions.append(search_q)

    if category_id and category_id not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(category_id=category_id))
        else:
            base_queryset = base_queryset.filter(category_id=category_id)
    if priority and priority not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(priority=priority))
        else:
            base_queryset = base_queryset.filter(priority=priority)
    if status and status not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(status=status))
        else:
            base_queryset = base_queryset.filter(status=status)
    if department and department not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(department=department))
        else:
            base_queryset = base_queryset.filter(department=department)
    if response_status and response_status not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(responses__response_status=response_status))
        else:
            base_queryset = base_queryset.filter(responses__response_status=response_status)
    if created_at_from:
        if search_mode == 'or':
            filter_conditions.append(Q(created_at__date__gte=created_at_from))
        else:
            base_queryset = base_queryset.filter(created_at__date__gte=created_at_from)
    if created_at_to:
        if search_mode == 'or':
            filter_conditions.append(Q(created_at__date__lte=created_at_to))
        else:
            base_queryset = base_queryset.filter(created_at__date__lte=created_at_to)
    if max_replay_date_from:
        if search_mode == 'or':
            filter_conditions.append(Q(max_replay_date__date__gte=max_replay_date_from))
        else:
            base_queryset = base_queryset.filter(max_replay_date__date__gte=max_replay_date_from)
    if max_replay_date_to:
        if search_mode == 'or':
            filter_conditions.append(Q(max_replay_date__date__lte=max_replay_date_to))
        else:
            base_queryset = base_queryset.filter(max_replay_date__date__lte=max_replay_date_to)

    if seen and seen not in ["", "None"]:
        if seen == 'yes':
            if search_mode == 'or':
                filter_conditions.append(Q(seen_at__isnull=False))
            else:
                base_queryset = base_queryset.filter(seen_at__isnull=False)
        elif seen == 'no':
            if search_mode == 'or':
                filter_conditions.append(Q(seen_at__isnull=True))
            else:
                base_queryset = base_queryset.filter(seen_at__isnull=True)

    if filter_conditions:
        if search_mode == 'or':
            combined_q = Q()
            for condition in filter_conditions:
                combined_q |= condition
            base_queryset = base_queryset.filter(combined_q).distinct()
        else:
            # حالت AND: فقط شرط جستجو اعمال می‌شود (بقیه قبلاً اعمال شده‌اند)
            if search_query:
                base_queryset = base_queryset.filter(search_q)


    from django.db.models import Exists, OuterRef

    tickets_with_access = base_queryset.annotate(
        is_assignee=Exists(
            Assignment.objects.filter(
                assigned_ticket=OuterRef('pk'),
                assignee=request.user
            )
        )
    ).select_related('category', 'created_by', 'seen_by') \
        .prefetch_related('tags', 'responses', 'assignments_tickets__assignee')


    if sort:
        if direction == 'desc':
            tickets_with_access = tickets_with_access.order_by('-' + sort)
        else:
            tickets_with_access = tickets_with_access.order_by(sort)
    else:

        tickets_with_access = tickets_with_access.order_by('seen_at', '-created_at')

    # Pagination
    paginator = Paginator(tickets_with_access, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # دریافت تیکت‌ها
    tickets = Ticket.objects.all()


    ticket_extra_info = []

    # for ticket in page_obj:
    #     # محاسبه وضعیت seen برای کاربر جاری
    #     is_seen_by_current_user = ticket.check_seen_by_user(request.user)
    #
    #     # بررسی دسترسی کاربر
    #     user_has_access = False
    #     if request.user.is_superuser:
    #         user_has_access = True
    #     elif ticket.created_by == request.user:
    #         user_has_access = True
    #     elif ticket.assignments_tickets.filter(assignee=request.user).exists():
    #         user_has_access = True
    #
    #     # ذخیره اطلاعات
    #     ticket_extra_info.append({
    #         'ticket': ticket,
    #         'user_has_access': user_has_access,
    #         'is_seen_by_current_user': is_seen_by_current_user,
    #         'is_unseen_for_current_user': not is_seen_by_current_user and user_has_access,
    #         'user_role': user_role,
    #     })

    for ticket in page_obj:
        # محاسبه وضعیت seen برای کاربر جاری
        is_seen_by_current_user = ticket.check_seen_by_user(request.user)

        user_has_access = False
        if request.user.is_superuser:
            user_has_access = True
        elif ticket.created_by == request.user:
            user_has_access = True
        elif ticket.assignments_tickets.filter(assignee=request.user).exists():
            user_has_access = True

        seen_history_data = []


        if ticket.seen_at and ticket.seen_by:
            seen_history_data.append({
                'user': ticket.seen_by,
                'seen_at': ticket.seen_at,
                'role': 'Sender' if ticket.seen_by == ticket.created_by else 'Admin'
            })


        for assignment in ticket.assignments_tickets.filter(seen_at__isnull=False):
            seen_history_data.append({
                'user': assignment.assignee,
                'seen_at': assignment.seen_at,
                'role': 'Assignee'
            })


        seen_history_data.sort(key=lambda x: x['seen_at'], reverse=True)


        ticket_extra_info.append({
            'ticket': ticket,
            'user_has_access': user_has_access,
            'is_seen_by_current_user': is_seen_by_current_user,
            'is_unseen_for_current_user': not is_seen_by_current_user and user_has_access,
            'user_role': user_role,
            'seen_history_data': seen_history_data,
            'seen_history_count': len(seen_history_data),
        })

    # Bulk Delete Actions
    if request.method == 'POST':
        print("🚨 POST request received for bulk delete!")
        print(f"POST data: {request.POST}")

        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to perform this operation.')
            return redirect('tickets-login')

        # بررسی action
        action = request.POST.get('action', '').strip()
        print(f"Action from form: '{action}'")

        # منطق حذف تیکت‌های انتخاب شده
        if action == 'delete_selected':
            selected_tickets = request.POST.getlist('selected_tickets')
            print(f"Selected tickets: {selected_tickets}")

            if not selected_tickets:
                messages.warning(request, 'No tickets have been selected.')
                return redirect('tickets')


            deletable_tickets = []
            for ticket_id in selected_tickets:
                try:
                    ticket = Ticket.objects.get(id=ticket_id)

                    can_delete = False

                    if user_role == "Super Admin":
                        can_delete = True
                    elif ticket.created_by == request.user:
                        can_delete = True
                    elif Assignment.objects.filter(assigned_ticket=ticket, assignee=request.user).exists():
                        can_delete = True

                    if can_delete and ticket.seen_at is not None:
                        deletable_tickets.append(ticket_id)
                    elif can_delete and ticket.seen_at is None:
                        messages.error(request,
                                       f'Ticket #{ticket.tracking_code} has not been seen. Mark it as Seen first.')
                except Ticket.DoesNotExist:
                    continue

            if not deletable_tickets:
                messages.error(request, 'No tickets found to be deleted.')
                return redirect('tickets')

            try:
                with transaction.atomic():

                    TicketAttachment.objects.filter(ticket_id__in=deletable_tickets).delete()
                    Assignment.objects.filter(assigned_ticket_id__in=deletable_tickets).delete()
                    TicketResponse.objects.filter(ticket_id__in=deletable_tickets).delete()

                    count, _ = Ticket.objects.filter(id__in=deletable_tickets).delete()

                    messages.success(request, f'✅ {count} Selected tickets deleted.')
            except Exception as e:
                messages.error(request, f'Error deleting tickets: {str(e)}')

            return redirect('tickets')


        elif action == 'delete_all_tickets':
            if user_role != "Super Admin":
                messages.error(request, 'You do not have permission to delete all tickets.')
                return redirect('tickets')


            unseen_tickets = base_queryset.filter(seen_at__isnull=True)
            if unseen_tickets.exists():
                unseen_count = unseen_tickets.count()
                messages.error(request,
                               f'❌ {unseen_count} There are unseen tickets. Mark them as Seen first.')
                return redirect('tickets')

            try:
                with transaction.atomic():
                    TicketAttachment.objects.all().delete()
                    Assignment.objects.all().delete()
                    TicketResponse.objects.all().delete()
                    SearchLogSignal.objects.all().delete()

                    count, _ = Ticket.objects.all().delete()

                    messages.success(request, f'✅ {count} Selected tickets deleted.')
            except Exception as e:
                messages.error(request, f'Error deleting tickets: {str(e)}')

            return redirect('tickets')


        elif action == 'delete_filtered':

            unseen_tickets = base_queryset.filter(seen_at__isnull=True)
            if unseen_tickets.exists():
                unseen_count = unseen_tickets.count()
                messages.error(request,
                               f'❌ {unseen_count}There are unseen tickets. Mark them as Seen first.')
                return redirect('tickets')

            try:
                with transaction.atomic():
                    ticket_ids = list(base_queryset.values_list('id', flat=True))

                    if not ticket_ids:
                        messages.warning(request, 'There are no tickets to delete.')
                        return redirect('tickets')

                    TicketAttachment.objects.filter(ticket_id__in=ticket_ids).delete()
                    Assignment.objects.filter(assigned_ticket_id__in=ticket_ids).delete()
                    TicketResponse.objects.filter(ticket_id__in=ticket_ids).delete()

                    deleted_count, _ = base_queryset.delete()

                    messages.success(request, f'✅ {deleted_count}Filtered tickets deleted.')
            except Exception as e:
                messages.error(request, f'Error deleting tickets: {str(e)}')

            return redirect('tickets')

        else:
            print(f"❌ No valid delete action found")
            messages.error(request, 'The operation is undefined.')
            return redirect('tickets')


    swipers = Swiper.objects.filter(is_active=True).order_by('-created_at')

    columns = [
        ('row', 'Row'),
        ('tracking_code', 'Tracking Code'),
        ('subject', 'Subject'),
        ('created_by', 'Created By'),
        ('priority', 'Priority'),
        ('category__name', 'Category'),
        ('tags', 'Tags'),
        ('assignees', 'Assignees'),
        ('max_replay_date', 'Max Replay Date'),
        ('created_at', 'Created At'),
    ]

    context = {
        "page_title": "Tickets List | Ticketing ",
        'page_obj': page_obj,
        'ticket_extra_info': ticket_extra_info,
        'search_query': search_query,
        'selected_category': category_id if category_id not in ["", "None"] else "",
        'selected_priority': priority if priority not in ["", "None"] else "",
        'selected_status': status if status not in ["", "None"] else "",
        'selected_department': department if department not in ["", "None"] else "",
        'selected_response_status': response_status if response_status not in ["", "None"] else "",
        'selected_seen': seen if seen not in ["", "None"] else "",
        'search_mode': search_mode,
        'categories': Category.objects.active(),
        'priorities': Ticket._meta.get_field('priority').choices,
        'statuses': Ticket._meta.get_field('status').choices,
        'departments': Ticket._meta.get_field('department').choices,
        'response_statuses': [
            ('sent', 'Sent'),
            ('seen', 'Seen'),
            ('read', 'Read'),
            ('replied', 'Replied'),
        ],
        'seen_choices': [
            ('yes', 'Seen'),
            ('no', 'Unseen'),
        ],
        'with_close': with_close,
        'direction': direction,
        'sort': sort,
        'columns': columns,
        'created_at_from': created_at_from,
        'created_at_to': created_at_to,
        'max_replay_date_from': max_replay_date_from,
        'max_replay_date_to': max_replay_date_to,
        'swipers': swipers,
        'user': request.user,
        'user_role': user_role,

        # بررسی وجود فیلترهای فعال
        'has_active_filters': bool(
            search_query or category_id or priority or status or department or
            response_status or created_at_from or created_at_to or
            max_replay_date_from or max_replay_date_to or seen or with_close == "on"),
    }

    return render(request, template_name='index-table-card-assignment-BulkDelete-new-seen-2.html', context=context)


def ticket_create(request):
    user_role = request.session.get('role')
    if user_role == "Employee":
        messages.error(request, 'Staff cannot create new tickets.')
        return redirect('tickets')

    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to create a ticket.')
        return redirect('tickets-login')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, request=request)




        validation_errors = {}


        # boolean_rules = {
        #     "send_notification": ["boolean"],
        #     "send_email": ["boolean"],
        #     "send_sms": ["boolean"],
        # }

        # boolean_errors = validate(request.POST, request.FILES, boolean_rules)
        boolean_errors = validate(request.POST, request.FILES)
        # if boolean_errors:
        #     validation_errors.update(boolean_errors)


        ticket_rules = {
            'subject': ['required', 'min:10', 'max:200'],
            'description': ['required', 'min:20'],
            'contact_name': ['required', 'min:3', 'max:100'],
            'contact_email': ['required', 'email'],
            'contact_phone': ['required', 'phone'],
            'priority': ['required'],
            'category': ['required'],
            'department': ['required'],
            'max_replay_date': ['required', 'future_date'],
            'due_date': ['future_date'],
            'tags': ['required', 'min_items:1', 'max_items:5'],
            'users': ['required', 'min_items:1', 'max_items:10'],
            'attachments': [
                'max_files:5',
                'max_size:10',
                'file_type:application/pdf,image/jpeg,image/png,application/msword'
            ]
        }

        ticket_errors = validate(request.POST, request.FILES, ticket_rules)
        if ticket_errors:
            validation_errors.update(ticket_errors)


        if validation_errors:
            for field, error in validation_errors.items():
                form.add_error(field, error)


        if not validation_errors and form.is_valid():
            new_ticket = form.save(commit=False)
            new_ticket.created_by_id = request.user.id
            new_ticket.seen_count = 0
            new_ticket.save()


            files = request.FILES.getlist("attachments")
            for file in files:
                TicketAttachment.objects.create(
                    ticket=new_ticket,
                    file=file,
                    uploaded_by_id=request.user.id
                )

            form.save_m2m()

            # ارسال نوتیفیکیشن بر اساس انتخاب کاربر
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

                # # ارسال نوتیفیکیشن بر اساس تنظیمات کاربر
                # if form.cleaned_data.get('send_notification'):
                #     send_in_app_notification(user, new_ticket)
                #
                # if form.cleaned_data.get('send_email'):
                #     send_ticket_email(user, new_ticket)
                #
                # if form.cleaned_data.get('send_sms'):
                #     send_ticket_sms(user, new_ticket)

            Assignment.objects.bulk_create(assignments)

            messages.success(request, 'Your ticket has been created successfully!')
            return redirect('ticket_success', id=new_ticket.id)

        else:
            messages.error(request, 'Please fix the form errors.')

    else:
        form = TicketForm(request=request)

    return render(request, 'ticket_create.html', {
        "page_title": "Create New Ticket | Ticketing",
        'form': form,
        'PRIORITY_CHOICES': PRIORITY_CHOICES,
        'STATUS_CHOICES': STATUS_CHOICES,
        'PRIORITY_COLORS': PRIORITY_COLORS,
        'STATUS_COLORS': STATUS_COLORS,
    })


@login_required()
def ticket_details(request, id):
    ticket = get_object_or_404(
        Ticket.objects.select_related('category', 'created_by', 'seen_by')
        .prefetch_related('tags', 'ticket_attachments'),
        id=id
    )

    user_role = request.session.get("role", "User")
    user_has_access = False

    if user_role == "Super Admin":
        user_has_access = True
        print(f"DETAILS: 👑 SUPER ADMIN has access to ticket #{id}")
    elif user_role == "Admin":
        user_has_access = ticket.created_by == request.user
        print(f"DETAILS: 🔧 ADMIN access check: {user_has_access}")
    elif user_role == "Employee":
        user_has_access = (ticket.created_by == request.user or
                           ticket.assignments_tickets.filter(assignee=request.user).exists())
        print(f"DETAILS: 👨‍💼 EMPLOYEE access check: {user_has_access}")
    else:
        user_has_access = ticket.created_by == request.user

    if not user_has_access:
        messages.error(request, 'You do not have access to this ticket.')
        return redirect('tickets')


    is_seen_by_current_user = ticket.check_seen_by_user(request.user)


    first_seen_by_current_user = ticket.get_first_seen_by_user(request.user)

    is_creator = ticket.created_by == request.user

    assignments = ticket.assignments_tickets.select_related('assignee').all()


    activities = ticket.activities.all()


    all_tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    row_number = 0
    for i, t in enumerate(all_tickets, start=1):
        if t.id == ticket.id:
            row_number = i
            break

    attachments = ticket.ticket_attachments.all()


    notes = ticket.notes.all().select_related('created_by').order_by('-created_at')


    if not (request.user.is_staff or request.user.is_superuser or
            request.user.groups.filter(name='Staff').exists()):
        notes = notes.filter(is_private=False)

    note_form = TicketNoteForm()

    notes_with_assignee_status = []
    for note in notes:
        note_data = {
            'note': note,
            'is_assignee': ticket.assignments_tickets.filter(assignee=note.created_by).exists(),
            'is_ticket_creator': note.created_by == ticket.created_by,
            'can_edit': note.created_by == request.user,
            'can_delete': note.created_by == request.user,
        }
        notes_with_assignee_status.append(note_data)


    seen_history_data = []


    seen_info = ticket.get_all_seen_info()
    seen_history_data = seen_info.get('viewers', [])

    context = {
        "page_title": f"Ticket #{ticket.tracking_code} | Ticketing",
        'ticket': ticket,
        'attachments': attachments,
        'row_number': row_number,
        'is_seen': ticket.is_seen,
        'seen_at': ticket.seen_at,
        'seen_by': ticket.seen_by,
        'seen_by_display': ticket.seen_by_display,
        'seen_count': ticket.seen_count,
        'assignments': assignments,
        'activities': activities,
        'first_seen_by_current_user': first_seen_by_current_user,
        'is_creator': is_creator,
        'user_has_access': user_has_access,
        'is_seen_by_current_user': is_seen_by_current_user,
        'current_user': request.user,
        'note_form': note_form,
        'can_add_note': user_has_access,
        'notes_with_status': notes_with_assignee_status,
        'notes': notes,
        'seen_history_data': seen_history_data,
        'seen_history_count': len(seen_history_data),
        'first_view': seen_info.get('first_view'),
        'last_view': seen_info.get('last_view'),
    }

    return render(request, 'ticket-details.html', context)


@login_required()
def ticket_update(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    user_role = request.session.get("role", "User")
    has_access = False

    if user_role == "Super Admin":
        has_access = True
    elif user_role == "Admin":
        has_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_access = ticket.created_by == request.user
    else:
        has_access = ticket.created_by == request.user

    if not has_access:
        messages.error(request, 'You do not have access to edit this ticket.')
        return redirect('tickets')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket, request=request)


        validation_errors = {}

        #
        # boolean_rules = {
        #     "send_notification": ["boolean"],
        #     "send_email": ["boolean"],
        #     "send_sms": ["boolean"],
        # }

        # boolean_errors = validate(request.POST, request.FILES, boolean_rules)
        boolean_errors = validate(request.POST, request.FILES)
        # if boolean_errors:
        #     validation_errors.update(boolean_errors)


        ticket_rules = {
            'subject': ['required', 'min:10', 'max:200'],
            'description': ['required', 'min:20'],
            'contact_name': ['required', 'min:3', 'max:100'],
            'contact_email': ['required', 'email'],
            'contact_phone': ['required', 'phone'],
            'priority': ['required'],
            'category': ['required'],
            'department': ['required'],
            'max_replay_date': ['required', 'future_date'],
            'due_date': ['future_date'],
            'tags': ['required', 'min_items:1', 'max_items:5'],
            'users': ['required', 'min_items:1', 'max_items:10'],
            'attachments': [
                'max_files:5',
                'max_size:10',
                'file_type:application/pdf,image/jpeg,image/png,application/msword'
            ]
        }

        ticket_errors = validate(request.POST, request.FILES, ticket_rules)
        if ticket_errors:
            validation_errors.update(ticket_errors)


        if validation_errors:
            for field, error in validation_errors.items():
                form.add_error(field, error)

        if not validation_errors and form.is_valid():

            updated_ticket = form.save()

            # Handle new attachment on EDIT
            files = request.FILES.getlist("attachments")
            for file in files:
                TicketAttachment.objects.create(
                    ticket=updated_ticket,
                    file=file,
                    uploaded_by_id=request.user.id
                )

            # Handle Assignment
            selected_users = set(form.cleaned_data['users'])
            current_users = set(
                ticket.assignments_tickets.values_list('assignee_id', flat=True)
            )

            # Remove unassigned users
            Assignment.objects.filter(
                assigned_ticket=ticket,
                assignee_id__in=(current_users - set(u.id for u in selected_users)),
            ).delete()

            # Add New Assignments
            new_assignments = []
            for user in selected_users:
                if user.id not in current_users:
                    new_assignments.append(
                        Assignment(
                            assigned_ticket=ticket,
                            assignee=user,
                            assigned_by_id=request.user.id,
                            status='new'
                        )
                    )

            if new_assignments:
                Assignment.objects.bulk_create(new_assignments)

            messages.success(request, f'Ticket #{ticket.id} has been updated Successfully !!!')
            return redirect('tickets-details', id=ticket.id)
        else:
            messages.error(request, 'Please fix the form errors.')
    else:

        form = TicketForm(instance=ticket, request=request)

        current_assignees = ticket.assignments_tickets.values_list('assignee_id', flat=True)
        form.fields['users'].initial = list(current_assignees)

    return render(request, 'ticket_create.html', {
        "page_title": f"Edit Ticket #{ticket.tracking_code} | Ticketing",
        'form': form,
        'ticket': ticket,
        'attachments': ticket.ticket_attachments.all(),
        'is_edit': True,
    })


@login_required()
def ticket_delete(request, id):
    try:
        ticket = Ticket.objects.get(id=id)


        user_role = request.session.get("role", "User")
        has_access = False

        if user_role == "Super Admin":
            has_access = True
            print(f"DELETE: 👑 SUPER ADMIN deleting ticket #{id}")
        elif user_role == "Admin":
            has_access = ticket.created_by == request.user
        elif user_role == "Employee":
            # Employee فقط اگر creator باشه می‌تونه حذف کنه
            has_access = ticket.created_by == request.user
        else:
            has_access = ticket.created_by == request.user

        if not has_access:
            messages.error(request, 'You do not have access to delete this ticket.')
            return redirect('tickets')


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
    return render(request, 'ticket_success.html', {
        'ticket': ticket,
        "page_title": "Ticket Created Successfully | Ticketing"
    })


@login_required
def search_logs(request):
    try:
        user_role = request.session.get("role", "User")


        if user_role == "Super Admin":
            logs = SearchLogSignal.objects.all().select_related('category', 'user').order_by('-created_at')
            print(f"👑 SUPER ADMIN sees ALL search logs")
        else:

            logs = SearchLogSignal.objects.filter(user=request.user).select_related('category').order_by('-created_at')
            print(f"Found {logs.count()} logs for user {request.user.username}")

        paginator = Paginator(logs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            "page_title": "Search History | Ticketing",
            'page_obj': page_obj,
            'logs': page_obj.object_list,
            'user_authenticated': request.user.is_authenticated,
            'is_super_admin': user_role == "Super Admin",
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

    return render(request, 'registration/login-page.html', {
        'swipers': swipers,
        "page_title": "Login | Ticketing"
    })


def ticket_attachment_delete(request, id):
    attachment = get_object_or_404(TicketAttachment, id=id)
    ticket = attachment.ticket

    attachment.file.delete(save=False)
    attachment.delete()

    messages.success(request, 'Ticket Attachment Deleted Successfully')
    return redirect('tickets-update', id=ticket.id)


@login_required
def ticket_attachments_delete_all(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)


    user_role = request.session.get("role", "User")
    has_access = False

    if user_role == "Super Admin":
        has_access = True
    elif user_role == "Admin":
        has_access = ticket.created_by == request.user
    elif user_role == "Employee":
        # Employee فقط اگر creator باشه می‌تونه حذف کنه
        has_access = ticket.created_by == request.user
    else:
        has_access = ticket.created_by == request.user

    if not has_access:
        messages.error(request, 'You do not have access to delete the files in this ticket.')
        return redirect('tickets-details', id=ticket.id)

    if request.method == 'POST':
        attachments = ticket.ticket_attachments.all()
        count = attachments.count()


        for attachment in attachments:
            attachment.file.delete(save=False)
            attachment.delete()

        messages.success(request, f'{count} attachment(s) deleted successfully')
        return redirect('tickets-update', id=ticket.id)


    return redirect('tickets-details', id=ticket.id)


@login_required
def download_all_attachments(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)


    user_role = request.session.get("role", "User")
    has_access = False

    if user_role == "Super Admin":
        has_access = True
    elif user_role == "Admin":
        has_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_access = (ticket.created_by == request.user or
                      ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_access = ticket.created_by == request.user

    if not has_access:
        messages.warning(request, 'You do not have access to the files in this ticket.')
        return redirect('tickets')

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
                    filename = os.path.basename(attachment.file.name)
                    zip_file.writestr(filename, f.read())
            except Exception as e:
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
    return render(request, 'registration/register.html', {
        'form': form,
        "page_title": "Register | Ticketing"
    })


def ticket_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('tickets-login')


@login_required
def assignee_ticket_list(request):
    user_role = request.session.get("role", "User")

    print(f"DEBUG: assignee_ticket_list - User: {request.user}, Role: {user_role}")


    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to view Tasks.')
        return redirect('tickets-login')

    try:

        if user_role == "Super Admin":

            assignments = Assignment.objects.all().select_related(
                'assigned_ticket',
                "assigned_ticket__category",
                'assignee'
            )
            print(f"DEBUG: Super Admin sees ALL assignments, count: {assignments.count()}")

        else:

            assignments = Assignment.objects.filter(
                assignee=request.user
            ).select_related(
                'assigned_ticket',
                "assigned_ticket__category",
                'assignee'
            )
            print(f"DEBUG: {user_role} sees assignments FOR self, count: {assignments.count()}")

        assignments = assignments.order_by("-created_at")
        print(f"DEBUG: After ordering, count: {assignments.count()}")

        paginator = Paginator(assignments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        print(f"DEBUG: Pagination - Page: {page_number}, Objects on page: {len(page_obj)}")

        context = {
            "page_title": "Assigned Tickets | Ticketing",
            'page_obj': page_obj,
            'user_role': user_role,
            'is_super_admin': user_role == "Super Admin",
            'is_admin': user_role == "Admin",
            'is_employee': user_role == "Employee",
        }

        print(f"DEBUG: Rendering template with context")
        return render(request, "assignee/ticket_assignee_list.html", context=context)

    except Exception as e:
        print(f"ERROR in assignee_ticket_list: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'An error occurred while loading the page:: {str(e)}')
        return redirect('tickets')


@login_required
def assignee_ticket_detail(request, id):
    user_role = request.session.get("role", "User")

    print(f"DEBUG: assignee_ticket_detail - User: {request.user}, Role: {user_role}, Assignment ID: {id}")


    if not request.user.is_authenticated:
        messages.error(request, 'You must log in to view the Task.')
        return redirect('tickets-login')

    try:
        assignment = None

        if user_role == "Super Admin":
            print(f"DEBUG: Super Admin trying to access assignment {id}")
            # Super Admin به همه assignments دسترسی دارد
            assignment = get_object_or_404(
                Assignment.objects.select_related(
                    'assigned_ticket',
                    'assigned_ticket__category',
                    'assigned_ticket__created_by',
                    'assignee'
                ),
                id=id
            )
            print(
                f"DEBUG: Super Admin found assignment for ticket: {assignment.assigned_ticket.id if assignment.assigned_ticket else 'None'}")


            if assignment.assigned_ticket:
                print(f"DEBUG: Super Admin marking ticket as seen for themselves only")
                assignment.assigned_ticket.mark_as_seen_for_user(request.user)

        else:
            print(f"DEBUG: {user_role} trying to access assignment {id}")

            assignment = get_object_or_404(
                Assignment.objects.select_related(
                    'assigned_ticket',
                    'assigned_ticket__category',
                    'assigned_ticket__created_by',
                    'assignee'
                ),
                id=id,
                assignee=request.user
            )
            print(
                f"DEBUG: {user_role} found assignment for ticket: {assignment.assigned_ticket.id if assignment.assigned_ticket else 'None'}")


            if assignment.assigned_ticket:
                print(f"DEBUG: {user_role} marking ticket as seen for themselves")
                assignment.assigned_ticket.mark_as_seen_for_user(request.user)


                if not assignment.seen_at:
                    assignment.mark_as_seen(request.user)

        if not assignment:
            print(f"DEBUG: Assignment not found or no access")
            messages.error(request, 'The requested assignment was not found or you do not have access')
            return redirect('assignee-list')

        ticket = assignment.assigned_ticket

        if not ticket:
            print(f"DEBUG: Ticket not found for assignment {id}")
            messages.error(request, 'The corresponding ticket was not found.')
            return redirect('assignee-list')

        print(f"DEBUG: Processing assignment {id} for ticket {ticket.id}")

        if request.method == "POST":
            print(f"DEBUG: POST request received for assignment {id}")

            can_change_status = False

            if user_role == "Super Admin":
                can_change_status = True
                print(f"DEBUG: Super Admin can change status")
            else:

                can_change_status = assignment.assignee == request.user
                print(f"DEBUG: {user_role} can change status: {can_change_status}")

            if not can_change_status:
                messages.error(request, 'You do not have permission to change the status of this ticket.')
                return redirect('assignee-detail', id=assignment.id)


            old_status = assignment.status
            new_status = request.POST.get('status')
            assignment.status = new_status
            assignment.description = request.POST.get('description', '').strip()
            assignment.save()

            ActivityLog.objects.create(
                user=request.user,
                ticket=ticket,
                action='update_status',
                field='status',
                old_value=old_status,
                new_value=new_status,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, 'Ticket status was successfully updated.')
            return redirect('assignee-detail', id=assignment.id)


        notes = ticket.notes.all()
        if user_role not in ["Super Admin", "Admin"]:
            notes = notes.filter(
                Q(is_private=False) |
                Q(created_by=request.user)
            )

        print(f"DEBUG: Preparing context for template")
        context = {
            "page_title": f"Task Details - {ticket.tracking_code} | Ticketing",
            'status_choices': STATUS_CHOICES,
            'assignment': assignment,
            'ticket': ticket,
            'notes': notes,
            'note_form': TicketNoteForm(),
            'user_role': user_role,
            'is_super_admin': user_role == "Super Admin",
            'is_admin': user_role == "Admin",
            'is_employee': user_role == "Employee",

            'can_change_status': (
                    user_role == "Super Admin" or
                    assignment.assignee == request.user
            ),
            'can_add_note': (
                    user_role == "Super Admin" or
                    assignment.assignee == request.user
            ),
        }

        print(f"DEBUG: Rendering template with context")
        return render(request, "assignee/ticket_assignee_detail.html", context=context)

    except Exception as e:
        print(f"ERROR in assignee_ticket_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'An error occurred while loading the page:: {str(e)}')
        return redirect('assignee-list')


@login_required
@csrf_exempt
def mark_assignment_seen(request, assignment_id):

    try:
        assignment = Assignment.objects.get(id=assignment_id)


        if assignment.assignee != request.user:

            if request.user.is_superuser:

                if assignment.assigned_ticket:
                    assignment.assigned_ticket.mark_as_seen_for_user(request.user)

                return JsonResponse({
                    'success': True,
                    'message': 'Ticket viewed (only history recorded).',
                    'seen_status': 'viewed_by_admin',
                    'is_super_admin': True,
                    'is_assignee': False
                })

            return JsonResponse({
                'success': False,
                'message': 'You do not have access to this Assignment.'
            }, status=403)


        if not assignment.seen_at:
            assignment.seen_at = timezone.now()
            assignment.save(update_fields=['seen_at'])


            if assignment.assigned_ticket:
                assignment.assigned_ticket.mark_as_seen_for_user(request.user)

            return JsonResponse({
                'success': True,
                'message': 'Ticket successfully marked as viewed.',
                'seen_at': assignment.seen_at.strftime('%Y/%m/%d %H:%M'),
                'seen_status': 'seen_by_assignee',
                'is_assignee': True
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'This ticket has already been viewed.',
                'seen_at': assignment.seen_at.strftime('%Y/%m/%d %H:%M'),
                'seen_status': 'already_seen'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Server Error: {str(e)}'
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class MarkAssignmentSeenView(View):


    def post(self, request, assignment_id):
        try:
            print(f"POST request to mark assignment {assignment_id} as seen")


            data = json.loads(request.body) if request.body else {}
            print(f"Request data: {data}")

            assignment = get_object_or_404(Assignment, id=assignment_id)


            if assignment.assignee != request.user:
                return JsonResponse({
                    'success': False,
                    'message': 'Access denied'
                }, status=403)


            if not assignment.seen_at:
                assignment.seen_at = timezone.now()
                assignment.save(update_fields=['seen_at'])

                if assignment.assigned_ticket:
                    assignment.assigned_ticket.mark_as_seen(request.user)

                return JsonResponse({
                    'success': True,
                    'message': 'Marked as seen successfully',
                    'seen_at': assignment.seen_at.isoformat(),
                    'user': request.user.username
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Already seen',
                    'seen_at': assignment.seen_at.isoformat()
                })

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)


@login_required()
def get_ticket_seen_info(request, ticket_id):

    try:
        ticket = Ticket.objects.get(id=ticket_id)

        user_role = request.session.get("role", "User")
        has_access = False

        if user_role == "Super Admin":
            has_access = True
        elif user_role == "Admin":
            has_access = ticket.created_by == request.user
        elif user_role == "Employee":
            has_access = (ticket.created_by == request.user or
                          ticket.assignments_tickets.filter(assignee=request.user).exists())
        else:
            has_access = ticket.created_by == request.user

        if not has_access:
            return JsonResponse({'error': 'Access denied'}, status=403)

        seen_info = ticket.get_all_seen_info()


        formatted_info = {
            'total_views': seen_info['total_views'],
            'first_view': {
                'user': seen_info['first_view'].user.username if seen_info['first_view'] else None,
                'seen_at': seen_info['first_view'].seen_at.strftime('%Y/%m/%d %H:%M') if seen_info[
                    'first_view'] else None,
                'time_ago': timesince(seen_info['first_view'].seen_at) if seen_info['first_view'] else None
            } if seen_info['first_view'] else None,
            'last_view': {
                'user': seen_info['last_view'].user.username if seen_info['last_view'] else None,
                'seen_at': seen_info['last_view'].seen_at.strftime('%Y/%m/%d %H:%M') if seen_info[
                    'last_view'] else None,
                'time_ago': timesince(seen_info['last_view'].seen_at) if seen_info['last_view'] else None
            } if seen_info['last_view'] else None,
            'viewers': [
                {
                    'user': v['user'].username,
                    'full_name': v['user'].get_full_name() or v['user'].username,
                    'seen_at': v['seen_at'].strftime('%Y/%m/%d %H:%M'),
                    'time_ago': timesince(v['seen_at']),
                    'role': 'Sender' if v['user'] == ticket.created_by else 'Assignee' if v['is_assignee'] else 'User'
                }
                for v in seen_info['viewers']
            ],
            'current_user_first_seen': ticket.get_first_seen_by_user(request.user)
        }

        return JsonResponse({
            'success': True,
            'seen_info': formatted_info,
            'ticket_seen': ticket.is_seen,
            'seen_count': ticket.seen_count
        })

    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def add_ticket_note(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)


    user_role = request.session.get("role", "User")
    has_access = False

    if user_role == "Super Admin":
        has_access = True
    elif user_role == "Admin":
        has_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_access = (ticket.created_by == request.user or
                      ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_access = ticket.created_by == request.user

    if not has_access:
        return JsonResponse({
            'success': False,
            'message': 'You do not have the required access.'
        }, status=403)

    if request.method == 'POST':
        form = TicketNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.ticket = ticket
            note.created_by = request.user
            note.save()


            ActivityLog.objects.create(
                user=request.user,
                ticket=ticket,
                action='add_note',
                field='note',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return JsonResponse({
                'success': True,
                'message': 'Note added successfully.',
                'note_id': note.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please fill out the form correctly.',
                'errors': form.errors
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    }, status=400)


@login_required
def edit_ticket_note(request, note_id):

    note = get_object_or_404(TicketNote, id=note_id)
    ticket = note.ticket

    user_role = request.session.get("role", "User")
    has_ticket_access = False

    if user_role == "Super Admin":
        has_ticket_access = True
    elif user_role == "Admin":
        has_ticket_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_ticket_access = (ticket.created_by == request.user or
                             ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_ticket_access = ticket.created_by == request.user

    if not has_ticket_access:
        return JsonResponse({
            'success': False,
            'message': 'You do not have access to this ticket.'
        }, status=403)

    if not (request.user == note.created_by or user_role == "Super Admin"):
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to edit this note.'
        }, status=403)

    if request.method == 'POST':
        form = TicketNoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save()


            ActivityLog.objects.create(
                user=request.user,
                ticket=note.ticket,
                action='edit_note',
                field='note',
                old_value='Note edited.',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return JsonResponse({
                'success': True,
                'message': 'Note successfully edited.',
                'note_id': note.id
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    }, status=400)


@login_required
def delete_ticket_note(request, note_id):

    note = get_object_or_404(TicketNote, id=note_id)
    ticket = note.ticket

    user_role = request.session.get("role", "User")
    has_ticket_access = False

    if user_role == "Super Admin":
        has_ticket_access = True
    elif user_role == "Admin":
        has_ticket_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_ticket_access = (ticket.created_by == request.user or
                             ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_ticket_access = ticket.created_by == request.user

    if not has_ticket_access:
        return JsonResponse({
            'success': False,
            'message': 'You do not have access to this ticket.'
        }, status=403)


    if not (request.user == note.created_by or user_role == "Super Admin"):
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to delete this note.'
        }, status=403)

    if request.method == 'POST':
        ticket_id = note.ticket.id
        note.delete()


        ActivityLog.objects.create(
            user=request.user,
            ticket=note.ticket,
            action='delete_note',
            field='note',
            old_value='Note deleted.',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return JsonResponse({
            'success': True,
            'message': 'Note successfully deleted.'
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    }, status=400)


@login_required
def get_ticket_notes(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)


    user_role = request.session.get("role", "User")
    has_access = False

    if user_role == "Super Admin":
        has_access = True
    elif user_role == "Admin":
        has_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_access = (ticket.created_by == request.user or
                      ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_access = ticket.created_by == request.user

    if not has_access:
        return JsonResponse({
            'success': False,
            'message': 'You do not have the necessary access.'
        }, status=403)

    notes = ticket.notes.all()


    if not (request.user.is_staff or request.user.is_superuser or
            request.user.groups.filter(name='Staff').exists()):
        notes = notes.filter(is_private=False)

    notes_data = []
    for note in notes:
        notes_data.append({
            'id': note.id,
            'content': note.content,
            'is_private': note.is_private,
            'created_by': {
                'id': note.created_by.id,
                'username': note.created_by.username,
                'full_name': note.created_by.get_full_name(),
            },
            'created_at': note.created_at.strftime('%Y/%m/%d %H:%M'),
            'created_at_display': timesince(note.created_at),
            'can_edit': request.user == note.created_by or user_role == "Super Admin",
            'can_delete': request.user == note.created_by or user_role == "Super Admin",
        })

    return JsonResponse({
        'success': True,
        'notes': notes_data,
        'count': len(notes_data),
        'can_add_note': True,
        'user_is_staff': request.user.is_staff,
        'user_role': user_role,
    })


@login_required
def add_ticket_note_assignee(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    # ✅ بررسی دسترسی - Employee باید assignee باشد
    user_role = request.session.get("role", "User")
    has_access = False

    if user_role == "Super Admin":
        has_access = True
    elif user_role == "Admin":
        has_access = ticket.created_by == request.user
    elif user_role == "Employee":
        # Employee باید assignee باشد
        assignment = ticket.assignments_tickets.filter(assignee=request.user).first()
        has_access = assignment is not None
    else:
        has_access = ticket.created_by == request.user

    if not has_access:
        messages.error(request, 'You do not have access to this ticket.')
        return redirect('assignee-list')


    assignment = ticket.assignments_tickets.filter(assignee=request.user).first()
    if not assignment and user_role != "Super Admin":
        messages.error(request, 'You do not have access to this ticket.')
        return redirect('assignee-list')

    if request.method == 'POST':
        form = TicketNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.ticket = ticket
            note.created_by = request.user
            note.save()


            ActivityLog.objects.create(
                user=request.user,
                ticket=ticket,
                action='add_note',
                field='note',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, 'Note added successfully..')

            if assignment:
                return redirect('assignee-detail', id=assignment.id)
            else:
                return redirect('tickets-details', id=ticket_id)

    messages.error(request, 'Error adding note.')
    return redirect('assignee-list')


@login_required
def edit_ticket_note_assignee(request, note_id):

    note = get_object_or_404(TicketNote, id=note_id)
    ticket = note.ticket

    user_role = request.session.get("role", "User")
    has_ticket_access = False

    if user_role == "Super Admin":
        has_ticket_access = True
    elif user_role == "Admin":
        has_ticket_access = ticket.created_by == request.user
    elif user_role == "Employee":
        # Employee باید assignee باشد
        assignment = ticket.assignments_tickets.filter(assignee=request.user).first()
        has_ticket_access = assignment is not None
    else:
        has_ticket_access = ticket.created_by == request.user

    if not has_ticket_access:
        messages.error(request, 'You do not have access to this ticket.')
        return redirect('assignee-list')


    if not (request.user == note.created_by or user_role == "Super Admin"):
        messages.error(request, 'You do not have permission to edit this note.')
        return redirect('assignee-list')


    assignment = ticket.assignments_tickets.filter(assignee=request.user).first()

    if request.method == 'POST':
        form = TicketNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()


            ActivityLog.objects.create(
                user=request.user,
                ticket=note.ticket,
                action='edit_note',
                field='note',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, 'The note was successfully edited.')
            if assignment:
                return redirect('assignee-detail', id=assignment.id)
            else:
                return redirect('tickets-details', id=ticket.id)

    messages.error(request, 'Error editing note.')
    return redirect('assignee-list')


@login_required
def delete_ticket_note_assignee(request, note_id):

    note = get_object_or_404(TicketNote, id=note_id)
    ticket = note.ticket


    user_role = request.session.get("role", "User")
    has_ticket_access = False

    if user_role == "Super Admin":
        has_ticket_access = True
    elif user_role == "Admin":
        has_ticket_access = ticket.created_by == request.user
    elif user_role == "Employee":
        # Employee باید assignee باشد
        assignment = ticket.assignments_tickets.filter(assignee=request.user).first()
        has_ticket_access = assignment is not None
    else:
        has_ticket_access = ticket.created_by == request.user

    if not has_ticket_access:
        messages.error(request, 'You do not have access to this ticket.')
        return redirect('assignee-list')


    if not (request.user == note.created_by or user_role == "Super Admin"):
        messages.error(request, 'You do not have permission to delete this note.')
        return redirect('assignee-list')


    assignment = ticket.assignments_tickets.filter(assignee=request.user).first()

    if request.method == 'POST':
        note.delete()


        ActivityLog.objects.create(
            user=request.user,
            ticket=note.ticket,
            action='delete_note',
            field='note',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, 'The note was successfully deleted.')
        if assignment:
            return redirect('assignee-detail', id=assignment.id)
        else:
            return redirect('tickets-details', id=ticket.id)

    return redirect('assignee-list')


@login_required
@require_POST
def add_ticket_note_details(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)


    user_role = request.session.get("role", "User")
    has_access = False

    if user_role == "Super Admin":
        has_access = True
    elif user_role == "Admin":
        has_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_access = (ticket.created_by == request.user or
                      ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_access = ticket.created_by == request.user

    if not has_access:
        messages.error(request, 'You do not have the necessary access.')
        return redirect('tickets-details', id=ticket_id)

    if request.method == 'POST':
        form = TicketNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.ticket = ticket
            note.created_by = request.user
            note.save()


            ActivityLog.objects.create(
                user=request.user,
                ticket=ticket,
                action='add_note',
                field='note',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, 'Note added successfully.')
        else:
            messages.error(request, 'Please fill out the form correctly.')

    return redirect('tickets-details', id=ticket_id)


@login_required
@require_POST
def edit_ticket_note_details(request, note_id):

    note = get_object_or_404(TicketNote, id=note_id)
    ticket = note.ticket


    user_role = request.session.get("role", "User")
    has_ticket_access = False

    if user_role == "Super Admin":
        has_ticket_access = True
    elif user_role == "Admin":
        has_ticket_access = ticket.created_by == request.user
    elif user_role == "Employee":
        has_ticket_access = (ticket.created_by == request.user or
                             ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_ticket_access = ticket.created_by == request.user

    if not has_ticket_access:
        messages.error(request, 'You do not have access to this ticket.')
        return redirect('tickets-details', id=note.ticket.id)


    if not (request.user == note.created_by or user_role == "Super Admin"):
        messages.error(request, 'You do not have permission to edit this note.')
        return redirect('tickets-details', id=note.ticket.id)

    form = TicketNoteForm(request.POST, instance=note)
    if form.is_valid():
        form.save()


        ActivityLog.objects.create(
            user=request.user,
            ticket=note.ticket,
            action='edit_note',
            field='note',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, 'Note successfully edited..')
    else:
        messages.error(request, 'Error editing note.')

    return redirect('tickets-details', id=note.ticket.id)


@login_required
@require_POST
def delete_ticket_note_details(request, note_id):
    note = get_object_or_404(TicketNote, id=note_id)
    ticket_id = note.ticket.id


    user_role = request.session.get("role", "User")
    has_ticket_access = False

    if user_role == "Super Admin":
        has_ticket_access = True
    elif user_role == "Admin":
        has_ticket_access = note.ticket.created_by == request.user
    elif user_role == "Employee":
        has_ticket_access = (note.ticket.created_by == request.user or
                             note.ticket.assignments_tickets.filter(assignee=request.user).exists())
    else:
        has_ticket_access = note.ticket.created_by == request.user

    if not has_ticket_access:
        messages.error(request, 'You do not have access to this ticket.')
        return redirect('tickets-details', id=ticket_id)

    if not (request.user == note.created_by or user_role == "Super Admin"):
        messages.error(request, 'You do not have permission to delete this note.')
        return redirect('tickets-details', id=ticket_id)

    note.delete()


    ActivityLog.objects.create(
        user=request.user,
        ticket=note.ticket,
        action='delete_note',
        field='note',
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, 'The note was successfully deleted.')
    return redirect('tickets-details', id=ticket_id)


@login_required
@csrf_exempt
def mark_ticket_seen(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)


        if not ticket.user_has_access_to_view(request.user):
            return JsonResponse({
                'success': False,
                'message': 'You do not have the necessary access.'
            }, status=403)


        if ticket.mark_as_seen_for_user(request.user):

            from .models import Assignment
            is_assignee = Assignment.objects.filter(
                assigned_ticket=ticket,
                assignee=request.user
            ).exists()

            is_creator = ticket.created_by == request.user

            return JsonResponse({
                'success': True,
                'message': 'Ticket viewed.',
                'seen_at': timezone.now().isoformat(),
                'user_type': 'super_admin' if request.user.is_superuser else
                'creator' if is_creator else
                'assignee' if is_assignee else 'other',
                'ticket_id': ticket.id,
                'is_seen_for_current_user': True,
                'is_ticket_marked_seen': ticket.seen_at is not None
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Operation completed.',
                'is_seen_for_current_user': True
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error in Server: {str(e)}'
        }, status=500)


def mark_as_seen_for_user(self, user):
    from .models import TicketSeenHistory, Assignment

    try:
        print(f"\n=== DEBUG mark_as_seen_for_user ===")
        print(f"Ticket: #{self.id}, User: {user.username}")


        already_seen = TicketSeenHistory.objects.filter(ticket=self, user=user).exists()
        print(f"Already in TicketSeenHistory: {already_seen}")


        if not already_seen:
            TicketSeenHistory.objects.get_or_create(
                ticket=self,
                user=user,
                defaults={'seen_at': timezone.now()}
            )
            print(f"Added to TicketSeenHistory")


        assignment = Assignment.objects.filter(
            assigned_ticket=self,
            assignee=user
        ).first()

        is_assignee = assignment is not None
        print(f"Is assignee: {is_assignee}")

        is_creator = self.created_by == user
        print(f"Is creator: {is_creator}")


        if is_creator or is_assignee:

            if is_creator and not self.seen_at:
                self.seen_at = timezone.now()
                self.seen_by = user
                print(f"Updated ticket main fields for creator")


            if is_assignee and assignment and not assignment.seen_at:
                assignment.seen_at = timezone.now()
                assignment.save(update_fields=['seen_at'])
                print(f"Updated assignment seen_at for assignee")


                if not self.seen_at:
                    self.seen_at = timezone.now()
                    self.seen_by = user
                    print(f"Also updated ticket main fields for assignee")


        if user.is_superuser:
            print(f"Super Admin view recorded in history only")


        old_count = self.seen_count
        self.update_seen_count()
        print(f"seen_count: {old_count} -> {self.seen_count}")
        print("===\n")

        return True

    except Exception as e:
        print(f"Error in mark_as_seen_for_user: {str(e)}")
        return False


@login_required
def get_seen_history(request, ticket_id):
    try:
        print(f"DEBUG: Getting seen history for ticket {ticket_id}")
        ticket = Ticket.objects.get(id=ticket_id)

        if not (request.user.is_superuser or
                ticket.created_by == request.user or
                ticket.assignments_tickets.filter(assignee=request.user).exists()):
            print(f"DEBUG: Access denied for user {request.user}")
            return JsonResponse({
                'success': False,
                'message': 'You have the necessary access.'
            }, status=403)

        seen_history = []

        if ticket.seen_at and ticket.seen_by:
            seen_history.append({
                'user': {
                    'username': ticket.seen_by.username,
                    'full_name': ticket.seen_by.get_full_name() or ticket.seen_by.username
                },
                'seen_at': ticket.seen_at.isoformat(),
                'seen_at_display': ticket.seen_at.strftime('%Y/%m/%d %H:%M'),
                'role': 'Sender' if ticket.seen_by == ticket.created_by else 'Admin'
            })


        for assignment in ticket.assignments_tickets.filter(seen_at__isnull=False):
            seen_history.append({
                'user': {
                    'username': assignment.assignee.username,
                    'full_name': assignment.assignee.get_full_name() or assignment.assignee.username
                },
                'seen_at': assignment.seen_at.isoformat(),
                'seen_at_display': assignment.seen_at.strftime('%Y/%m/%d %H:%M'),
                'role': 'Assignee'
            })

        print(f"DEBUG: Found {len(seen_history)} seen records")

        return JsonResponse({
            'success': True,
            'ticket_id': ticket.id,
            'ticket_code': ticket.tracking_code,
            'seen_history': seen_history,
            'total_views': len(seen_history)
        })

    except Ticket.DoesNotExist:
        print(f"DEBUG: Ticket {ticket_id} not found")
        return JsonResponse({
            'success': False,
            'message': 'Not Found Ticket'
        }, status=404)
    except Exception as e:
        print(f"DEBUG: Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error in Server: {str(e)}'
        }, status=500)
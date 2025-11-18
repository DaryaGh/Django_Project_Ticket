from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from Tickets.models import *
from django.contrib.auth.models import User

@receiver(post_save, sender=Ticket)
def ticket_created_or_updated(sender, instance, created, **kwargs):
    if created:
        print(f" >> New Ticket Created : {instance.subject}")
    else:
        print(f" >> Ticket Updated : {instance.subject}")


@receiver(post_delete, sender=Ticket)
def ticket_deleted(sender, instance, **kwargs):
    print(f" >> Ticket Deleted : {instance.subject}")

    # در فایل app.py مراحل رجستر را انجام میدهیم

    # باید لاگ فایل درست کنید یا به صورت پنل اس ام اس باشه یا ایمیل

def create_search_log(user, search_data):
    search_query = search_data.get('q', '')
    category_id = search_data.get('category', '')
    priority = search_data.get('priority', '')
    status = search_data.get('status', '')
    department = search_data.get('department', '')
    response_status = search_data.get('response_status', '')
    search_mode = search_data.get('search_mode', 'and')
    with_close = search_data.get('with_close', '')

    if not user.is_authenticated:
        try:
            default_user, created = User.objects.get_or_create(
                username='anonymous',
                defaults={
                    'email': '',
                    'is_active': False,
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            user = default_user
            print("Using anonymous user for logging")
        except:
            print("Could not create anonymous user")
            return

    tickets = Ticket.objects if with_close == "on" else Ticket.objects.is_open()
    tickets = tickets.select_related('category', "created_by").prefetch_related('tags', 'responses')

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
            tickets = tickets.filter(category_id=category_id)

    if priority and priority not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(priority=priority))
        else:
            tickets = tickets.with_priority(priority)

    if status and status not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(status=status))
        else:
            tickets = tickets.by_status(status)

    if department and department not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(department=department))
        else:
            tickets = tickets.filter(department=department)

    if response_status and response_status not in ["", "None"]:
        if search_mode == 'or':
            filter_conditions.append(Q(responses__response_status=response_status))
        else:
            tickets = tickets.filter(responses__response_status=response_status)

    if filter_conditions:
        if search_mode == 'or':
            combined_q = Q()
            for condition in filter_conditions:
                combined_q |= condition
            tickets = tickets.filter(combined_q).distinct()
        else:
            if search_query:
                tickets = tickets.filter(search_q)

    elif search_mode == 'and' and not search_query and (category_id or priority or status or department or response_status ):
        pass

    results_count = tickets.count()

    try:
        category_obj = None
        if category_id and category_id not in ["", "None"]:
            try:
                category_obj = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        log = SearchLogSignal.objects.create(
            user=user,
            search_query=search_query,
            category=category_obj,
            priority=priority or '',
            status=status or '',
            department=department or '',
            response_status=response_status or '',
            search_mode=search_mode,
            results_count=results_count
        )
        print(f" Search log created: ID {log.id}, User: {user.username}, Query: '{search_query}', Results: {results_count}, Mode: {search_mode}")
    except Exception as e:
        print(f" Error creating search log: {e}")
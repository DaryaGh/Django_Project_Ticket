from django.db.models import Q
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from Tickets.middleware import *
from Tickets.models import *
from django.contrib.auth.models import User
from django.utils import timezone
# seen
from django.contrib.auth import get_user_model
# Email
from django.core.mail import send_mail
# Email-With-Template
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


@receiver(post_save, sender=Ticket)
def ticket_email_notification(sender, instance, created, **kwargs):
    if created:
        subject = f"New Ticket Created : #{instance.tracking_code}"
        html_template = 'emails/ticket-email-create.html'
        text_template = 'emails/ticket-email-create.txt'
    else:
        subject = f"New Ticket Updated : #{instance.tracking_code}"
        html_template = 'emails/ticket-email-update.html'
        text_template = 'emails/ticket-email-update.txt'

    context = {
        'ticket' : instance,
        'creator' : instance.created_by,
        'ticket_url' : f'http://127.0.0.1:8000/Tickets/#{instance.tracking_code}/',
    }

    text_content = render_to_string(text_template, context)
    html_content = render_to_string(html_template, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        # from_email = settings.DEFAULT_FROM_EMAIL,
        from_email = None,
        # to=[instance.created_by.email],
        # to=["D.Ghaffary@hotmail.com"],
        to=["daryaaa.ghaffary@gmail.com"],
    )

    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


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


@receiver(post_save, sender=Assignment)
def mark_assignment_seen(sender, instance, created, **kwargs):
    if created:
        instance.seen_at = timezone.now()
        instance.save(update_fields=['seen_at'])

@receiver(post_save, sender=get_user_model())
def update_ticket_seen_by_display(sender, instance, **kwargs):
    tickets = Ticket.objects.filter(seen_by=instance)
    for ticket in tickets:
        ticket.save()


@receiver(pre_save, sender=Ticket)
def log_ticket_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Ticket.objects.get(pk=instance.pk)
    user = get_current_user()
    ip = get_current_ip()

    tracked_fields = ["subject" , "priority" , "description"]

    for field in tracked_fields:
        old_value = getattr(old, field)
        new_value = getattr(instance, field)

        if old_value != new_value:
            ActivityLog.objects.create(
                user=user,
                ticket=instance,
                # action="status_change" if field == "status" else "update",
                action="update",
                field=field,
                old_value=str(old_value),
                new_value=str(new_value),
                ip_address=ip,
            )





# Email ==> Example-2

# @receiver(post_save, sender=Ticket)
# def ticket_email_notification(sender, instance, created, **kwargs):
#     recipient_list = []
#     subject = ""
#     message = ""
#     if created:
#         subject = f"New Ticket Created : #{instance.tracking_code}"
#         message = (
#             f"A new ticket has been created for {instance.tracking_code}. \n\n"
#             f"Description : {instance.description}\n"
#             f"Title  : {instance.subject}\n"
#             f"Created by : {instance.created_by.username}\n"
#             f"Created at : {instance.created_at}\n"
#         )

#         if instance.contact_email:
#             recipient_list = [instance.contact_email]
#         elif instance.created_by and instance.created_by.email:
#             recipient_list = [instance.created_by.email]
#         else:
#             recipient_list = ['d.ghaffary@hotmail.com']
#
#     else:
#         subject = f"Ticket Updated : #{instance.tracking_code}"
#         message = (
#             f"Ticket has been Updated : #{instance.tracking_code}\n\n"
#             f"Description : {instance.description}\n"
#             f"Title  : {instance.subject}\n"
#             f"Last updated at : {instance.updated_at}\n"
#         )
#         # recipient_list = ['admin@yourdomain.com', 'support@yourdomain.com']
#     if recipient_list and all(recipient_list):
#         try:
#             # from_email = settings.DEFAULT_FROM_EMAIL or 'noreply@yourdomain.com'
#             from_email = settings.DEFAULT_FROM_EMAIL
#
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=from_email,
#                 recipient_list=recipient_list,
#                 fail_silently=True
#             )
#         except Exception as e:
#             print(f"❌ خطا در ارسال ایمیل برای تیکت #{instance.tracking_code}: {e}")
#     else:
#         print(f"⚠️ آدرس ایمیل گیرنده معتبری برای تیکت #{instance.tracking_code} یافت نشد")
#


# Email ==> Example-1

# @receiver(post_save, sender=Ticket)
# def ticket_email_notification(sender, instance, created, **kwargs):
#     if created:
#         subject = f"New Ticket Created : #{instance.tracking_code}"
#         message = (
#             f"A new ticket has been created.\n\n"
#             f"Description : {instance.description}\n"
#             f"Title  : {instance.subject}\n"
#             f"Created by : {instance.created_by.username}\n"
#             f"Created at : {instance.created_at}\n"
#         )
#     else:
#         subject = f"Ticket Updated from {instance.tracking_code}"
#         message = (
#             f"A new ticket has been Updated.\n\n"
#             f"Description : {instance.description}\n"
#             f"Title  : {instance.subject}\n"
#             f"Created by : {instance.created_by.username}\n"
#             f"Created at : {instance.created_at}\n"
#         )
#     send_mail(
#         subject=subject,
#         message=message,
#         # خودش میره میخونه
#         from_email=None,
#         # recipient_list=[instance.created_by.username],
#         recipient_list=["D.Ghaffary@hotmail.com"],
#         fail_silently=False,
#     )
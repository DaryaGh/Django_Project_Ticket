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
    search_mode = search_data.get('search_mode', 'and')

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
            print("👤 Using anonymous user for logging")
        except:
            print("❌ Could not create anonymous user")
            return

    tickets = Ticket.objects.is_open()

    if search_query:
        search_q = Q(
            Q(subject__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tracking_code__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
        tickets = tickets.filter(search_q)

    if category_id and category_id not in ["", "None"]:
        tickets = tickets.filter(category_id=category_id)

    if priority and priority not in ["", "None"]:
        tickets = tickets.with_priority(priority)

    results_count = tickets.count()

    try:
        category_obj = None
        if category_id and category_id not in ["", "None"]:
            try:
                category_obj = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        log = SearchLog.objects.create(
            user=user,
            search_query=search_query,
            category=category_obj,
            priority=priority or '',
            search_mode=search_mode,
            results_count=results_count
        )
        print(f"✅ Search log created: ID {log.id}, User: {user.username}, Query: '{search_query}'")
    except Exception as e:
        print(f"❌ Error creating search log: {e}")
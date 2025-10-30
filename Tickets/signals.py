from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from Tickets.models import Ticket


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
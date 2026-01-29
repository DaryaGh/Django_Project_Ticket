from django.core.mail import send_mail
from django.conf import settings

def send_in_app_notification(user, ticket):
    """ارسال نوتیفیکیشن درون اپلیکیشن"""
    # اینجا می‌توانید از سیستم نوتیفیکیشن داخلی جنگو یا یک پکیج استفاده کنید
    # مثال: django-notifications-hq
    try:
        from notifications.signals import notify

        notify.send(
            sender=ticket.created_by,
            recipient=user,
            verb='assigned you to a new ticket',
            action_object=ticket,
            description=f'You have been assigned to ticket: {ticket.subject}'
        )
        return True
    except ImportError:
        # اگر پکیج نصب نیست، لاگ کنید
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Notification package not installed")
        return False

def send_ticket_email(user, ticket):
    """ارسال ایمیل در مورد تیکت"""
    try:
        subject = f'New Ticket Assignment: {ticket.subject}'
        message = f'''
        Dear {user.get_full_name() or user.username},

        You have been assigned to a new ticket:

        Ticket ID: {ticket.id}
        Subject: {ticket.subject}
        Priority: {ticket.get_priority_display()}
        Description: {ticket.description[:200]}...

        Please login to the system to view and respond to this ticket.

        Regards,
        Support Team
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending email: {e}")
        return False

def send_ticket_sms(user, ticket):
    """ارسال SMS در مورد تیکت"""
    # این بخش بستگی به سرویس SMS شما دارد
    # مثال با استفاده از یک سرویس فرضی
    try:
        # کد ارسال SMS با استفاده از API سرویس‌دهنده
        # مثل کافه‌نگار، پیامک و ...
        phone_number = user.profile.phone if hasattr(user, 'profile') else None

        if phone_number:
            # اینجا API سرویس SMS را فراخوانی کنید
            # sms_service.send(phone_number, f"New ticket: {ticket.subject}")
            return True
        return False
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending SMS: {e}")
        return False
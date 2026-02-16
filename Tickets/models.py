from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify, capfirst
from django.utils.timezone import now
from .Choices import *
from django.contrib.auth.models import User
import uuid


class TimestampedModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    class Meta:
        abstract = True

class NameSlugModel(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)  # web development => web-development
        super().save(*args, **kwargs)

    def __str__(self):
        return capfirst(self.name)

class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

class Category(NameSlugModel):
    # is_active = models.BooleanField(default=True)
    pass

    class Meta:
        # برای ادمین پنل دیگه S اضافه نگیره
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

        # برای دیتابیس
        db_table = 'Tickets-Categories'

    objects = CategoryQuerySet.as_manager()

class Tag(NameSlugModel):
    is_approved = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)

    class Meta:
        # برای ادمین پنل دیگه S اضافه نگیره
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

        # برای دیتابیس
        db_table = 'Tickets-Tags'

    # def __str__(self):
    #     return capfirst(self.name)

class TicketQuerySet(models.QuerySet):
    def with_priority(self,priority):
        return self.filter(priority=priority)

    def is_close(self):
        # دارای تاریخ برای تمام شدن پروژه نیستند
        # return self.filter(closed_at__isnull=True)

        # دارای تاریخ برای تمام شدن پروژه هستند
        # return self.filter(closed_at__isnull=False)

        # دارای تاریخ برای تمام شدن پروژه هستند
        return self.exclude(closed_at__isnull=True)

    def is_open(self):
        return self.filter(closed_at__isnull=True)

    def is_expired(self):
        # return self.filter(expired_at__isnull=True)
        return self.filter(
            max_replay_date__lt=timezone.now(),
            closed_at__isnull=True
        )

    def max_replay_date(self):
        return self.order_by('-max_replay_date')

    def assigned_by(self):
        return self.filter(created_by=settings.AUTH_USER_MODEL)

    def by_status(self,status):
        return self.filter(status=status)

    def by_department(self,department):
        return self.filter(department=department)

    def with_tags(self, *tag_names):
        # تیکت‌هایی که دارای تگ‌های مشخص هستند
        return self.filter(tags__name__in=tag_names).distinct()

class Ticket(TimestampedModel):
    category = models.ForeignKey(Category, related_name='tickets', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.PROTECT,default=None, blank=True, null=True)
    priority = models.CharField(max_length=100, choices=PRIORITY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name='tickets', blank=True)
    max_replay_date = models.DateTimeField(help_text="The maximum replay date the ticket will reply")
    closed_at = models.DateTimeField(null=True, blank=True)
    tracking_code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    published_at = models.DateTimeField(null=True, blank=True)
    contact_name = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    due_date = models.DateTimeField(null=True, blank=True)
    seen_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='seen_tickets', on_delete=models.SET_NULL,null=True, blank=True)
    seen_at = models.DateTimeField(null=True, blank=True)
    seen_count = models.PositiveIntegerField(default=0)
    send_notification = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        db_table = 'Tickets-Ticket'

        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['priority']),
        ]

        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new and not self.tracking_code:
            temp_tracking_code = f"TCK-TEMP-{uuid.uuid4().hex[:8].upper()}"
            self.tracking_code = temp_tracking_code

        super().save(*args, **kwargs)
        if is_new:
            final_tracking_code = f"TCK-{now().strftime('%Y%m%d')}-{self.pk:05d}"
            if self.tracking_code.startswith('TCK-TEMP-'):
                Ticket.objects.filter(pk=self.pk).update(tracking_code=final_tracking_code)
                self.tracking_code = final_tracking_code

    def get_priority_color(self):
        return PRIORITY_COLORS.get(self.priority, '#6c757d')

    def get_status_color(self):
        return STATUS_COLORS.get(self.status, '#6c757d')

    def get_department_color(self):
        return DEPARTMENT_COLORS.get(self.department, '#6c757d')

    def get_edit_url(self):
        return reverse('tickets-update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('tickets-details', args=[self.pk])

    def get_delete_url(self):
        return reverse('tickets-destroy', args=[self.pk])

    def get_tickets_url(self):
        return reverse('tickets', args=[self.pk])

    def delete(self, *args, **kwargs):
        if self.priority == 'high':
            raise PermissionDenied("Cannot delete tickets with HIGH priority")
        super().delete(*args, **kwargs)

    def get_assigned_users(self):
        return self.assignments_tickets.all().values_list('assignee__username', flat=True)

    def get_assigned_users_count(self):
        return self.assignments_tickets.count()

    def get_assigned_users_display(self):
        users = self.get_assigned_users()
        if users:
            return ", ".join(users)
        return "-"

    def get_first_seen_by_user(self, user):
        from .models import TicketSeenHistory

        try:
            seen_history = TicketSeenHistory.objects.filter(
                ticket=self,
                user=user
            ).order_by('seen_at').first()

            if seen_history:
                return seen_history.seen_at
        except Exception:
            pass


        if self.seen_by == user and self.seen_at:
            return self.seen_at

        # اگر کاربر Assignee است
        from .models import Assignment
        assignment = Assignment.objects.filter(
            assigned_ticket=self,
            assignee=user,
            seen_at__isnull=False
        ).order_by('seen_at').first()

        if assignment and assignment.seen_at:
            return assignment.seen_at

        return None

    def get_all_seen_info(self):

        from .models import Assignment, TicketSeenHistory

        seen_info = {
            'total_views': 0,
            'first_view': None,
            'last_view': None,
            'viewers': []
        }

        viewers = []

        # 1. بررسی TicketSeenHistory
        seen_history_entries = TicketSeenHistory.objects.filter(ticket=self)
        for entry in seen_history_entries:
            seen_info['total_views'] += 1
            viewer_info = {
                'user': entry.user,
                'seen_at': entry.seen_at,
                'is_assignee': self.assignments_tickets.filter(assignee=entry.user).exists(),
                'is_ticket_creator': entry.user == self.created_by,
                'source': 'seen_history'
            }
            viewers.append(viewer_info)

        # 2. بررسی فیلدهای اصلی تیکت
        if self.seen_at and self.seen_by:
            # اگر کاربر در تاریخچه نبود، اضافه کن
            if not any(v['user'] == self.seen_by for v in viewers):
                seen_info['total_views'] += 1
                viewer_info = {
                    'user': self.seen_by,
                    'seen_at': self.seen_at,
                    'is_assignee': self.assignments_tickets.filter(assignee=self.seen_by).exists(),
                    'is_ticket_creator': self.seen_by == self.created_by,
                    'source': 'ticket_fields'
                }
                viewers.append(viewer_info)

        # 3. بررسی Assigneeها
        for assignment in self.assignments_tickets.filter(seen_at__isnull=False):
            # اگر کاربر در تاریخچه نبود، اضافه کن
            if not any(v['user'] == assignment.assignee for v in viewers):
                seen_info['total_views'] += 1
                viewer_info = {
                    'user': assignment.assignee,
                    'seen_at': assignment.seen_at,
                    'is_assignee': True,
                    'is_ticket_creator': assignment.assignee == self.created_by,
                    'source': 'assignment'
                }
                viewers.append(viewer_info)

        # مرتب‌سازی بر اساس تاریخ
        viewers.sort(key=lambda x: x['seen_at'])

        if viewers:
            seen_info['first_view'] = viewers[0]  # اولین
            seen_info['last_view'] = viewers[-1]  # آخرین
            seen_info['viewers'] = viewers

        return seen_info

    def mark_as_seen(self, user):
        """متد backward compatibility برای mark_as_seen"""
        return self.mark_as_seen_for_user(user)

    @property
    def seen_by_current_user(self):

        from .models import Assignment

        if not hasattr(self, '_request_user'):
            return False

        user = self._request_user

        if user.is_superuser:
            return self.seen_at is not None

        if self.created_by == user:
            return self.seen_at is not None

        assignment = Assignment.objects.filter(
            assigned_ticket=self,
            assignee=user
        ).first()

        if assignment:
            return assignment.seen_at is not None

        return False

    @property
    def is_seen(self):
        """بررسی آیا تیکت دیده شده است"""
        return self.seen_at is not None

    @property
    def seen_by_display(self):
        """نمایش نام کاربری که تیکت را دیده است"""
        if self.seen_by:
            return self.seen_by.get_full_name() or self.seen_by.username
        return "هنوز دیده نشده"

    def calculate_seen_count(self):
        """محاسبه تعداد دیده شدن‌ها - نسخه دیباگ"""
        from .models import TicketSeenHistory, Assignment

        print(f"\n=== DEBUG calculate_seen_count for Ticket #{self.id} ===")

        # 1. بررسی TicketSeenHistory
        seen_history = TicketSeenHistory.objects.filter(ticket=self)
        print(f"TicketSeenHistory entries: {seen_history.count()}")
        for entry in seen_history:
            print(f"  - User: {entry.user.username}, Seen at: {entry.seen_at}")

        # 2. بررسی فیلدهای اصلی
        print(f"Ticket main fields - seen_at: {self.seen_at}, seen_by: {self.seen_by}")

        # 3. بررسی Assignments
        assignments = Assignment.objects.filter(assigned_ticket=self, seen_at__isnull=False)
        print(f"Assignments with seen_at: {assignments.count()}")
        for assignment in assignments:
            print(f"  - Assignee: {assignment.assignee.username}, Seen at: {assignment.seen_at}")


        unique_users = set()

        # اضافه کردن کاربران از TicketSeenHistory
        for entry in seen_history:
            unique_users.add(entry.user.id)

        # اضافه کردن seen_by از فیلدهای اصلی
        if self.seen_by:
            unique_users.add(self.seen_by.id)

        # اضافه کردن assigneeها
        for assignment in assignments:
            unique_users.add(assignment.assignee.id)

        print(f"Unique users who saw this ticket: {len(unique_users)}")
        print(f"Unique user IDs: {unique_users}")
        print("===\n")

        return len(unique_users)

    def update_seen_count(self):
        """آپدیت فیلد seen_count"""
        old_count = self.seen_count
        self.seen_count = self.calculate_seen_count()

        if old_count != self.seen_count:
            print(f"DEBUG: Ticket #{self.id} - seen_count changed: {old_count} -> {self.seen_count}")

        self.save(update_fields=['seen_count'])

    def check_seen_by_user(self, user):
        """بررسی آیا تیکت توسط کاربر خاص دیده شده است"""
        # بررسی TicketSeenHistory
        from .models import TicketSeenHistory, Assignment

        # چک کردن از تاریخچه
        if TicketSeenHistory.objects.filter(ticket=self, user=user).exists():
            return True

        # چک کردن از فیلدهای اصلی (فقط برای کاربرانی که Assignee یا Creator هستند)
        if self.seen_by == user and self.seen_at:
            return True

        # چک کردن از Assignment (فقط برای Assigneeها)
        if Assignment.objects.filter(
                assigned_ticket=self,
                assignee=user,
                seen_at__isnull=False
        ).exists():
            return True

        return False

    @property
    def user_has_access(self):
        """بررسی آیا کاربر جاری به این تیکت دسترسی دارد"""
        if not hasattr(self, '_request_user'):
            return False

        user = self._request_user

        if user.is_superuser:
            return True

        if self.created_by == user:
            return True

        if self.assignments_tickets.filter(assignee=user).exists():
            return True

        return False

    @property
    def is_seen_by_current_user(self):
        """بررسی آیا تیکت توسط کاربر جاری دیده شده است"""
        if not hasattr(self, '_current_user_seen_cache'):
            self._current_user_seen_cache = False

        user = self._request_user if hasattr(self, '_request_user') else None

        if not user or not user.is_authenticated:
            return False

        return self.check_seen_by_user(user)

    def mark_as_seen_for_user(self, user):
        """علامت‌گذاری تیکت به عنوان دیده شده توسط کاربر خاص"""
        from .models import TicketSeenHistory

        # ایجاد رکورد در تاریخچه دیده شدن‌ها برای هر کاربری که می‌بیند
        # اما فقط کاربرانی که حق دیدن دارند
        if self.user_has_access_to_view(user):
            # ایجاد رکورد در TicketSeenHistory برای کاربر فعلی
            TicketSeenHistory.objects.get_or_create(
                ticket=self,
                user=user,
                defaults={'seen_at': timezone.now()}
            )

            # فقط برای کاربرانی که Assignee هستند یا Creator، فیلدهای اصلی را آپدیت کن
            # Super Admin فیلدهای اصلی را آپدیت نمی‌کند

            # برای ایجادکننده
            if self.created_by == user:
                if not self.seen_at:
                    self.seen_at = timezone.now()
                    self.seen_by = user
                    self.save(update_fields=['seen_at', 'seen_by'])
                return True

            # برای Assignee
            from .models import Assignment
            assignment = Assignment.objects.filter(
                assigned_ticket=self,
                assignee=user
            ).first()

            if assignment and not assignment.seen_at:
                assignment.seen_at = timezone.now()
                assignment.save(update_fields=['seen_at'])

                # همچنین Ticket اصلی را هم mark_as_seen کن (فقط برای Assignee)
                if not self.seen_at:
                    self.seen_at = timezone.now()
                    self.seen_by = user
                    self.save(update_fields=['seen_at', 'seen_by'])
                return True

            # برای Super Admin - فقط تاریخچه را ثبت می‌کنیم، فیلدهای اصلی را تغییر نمی‌دهیم
            if user.is_superuser:
                return True

        return True  # چون در TicketSeenHistory ثبت شد

    def user_has_access_to_view(self, user):
        """بررسی آیا کاربر حق دیدن این تیکت را دارد"""
        if user.is_superuser:
            return True

        if self.created_by == user:
            return True

        from .models import Assignment
        if Assignment.objects.filter(assigned_ticket=self, assignee=user).exists():
            return True

        return False

    def __str__(self):
        return f"#{self.tracking_code} {self.subject[:30]}..."

    objects = TicketQuerySet.as_manager()

class TicketResponse(TimestampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='responses')
    message = models.TextField()
    response_status = models.CharField(max_length=10, choices=RESPONSE_STATUS_CHOICES, default='sent')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply_to = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True,related_name='replies')
    is_internal_note = models.BooleanField(default=False, verbose_name='Internal note')

    class Meta:
        db_table = 'Tickets-Responses'
        ordering = ['created_at']
        permissions = [
            ('can_reply_all', 'Can reply to all'),
            ('can_edit_own', 'Can edit own messages'),
            ('can_delete_own', 'Can delete own messages'),
        ]

    def get_response_status_color(self):
        return RESPONSE_STATUS_COLORS.get(self.response_status, '#6c757d')

    def can_user_edit(self, user):
        """بررسی آیا کاربر می‌تواند این پیام را ویرایش کند"""
        # فقط ایجادکننده پیام می‌تواند ویرایش کند
        return user == self.created_by

    def can_user_delete(self, user):
        """بررسی آیا کاربر می‌تواند این پیام را حذف کند"""
        # فقط ایجادکننده پیام می‌تواند حذف کند
        return user == self.created_by

    def can_user_reply(self, user):
        """بررسی آیا کاربر می‌تواند به این پیام پاسخ دهد"""
        # همه کاربران مجاز می‌توانند پاسخ دهند
        return (
                user == self.ticket.created_by or
                self.ticket.assignments_tickets.filter(assignee=user).exists() or
                user.is_staff or
                user.is_superuser
        )

    def is_original_poster(self, user):
        """آیا کاربر فرستنده اصلی این پیام است؟"""
        return user == self.created_by

    def get_reply_info(self):
        """دریافت اطلاعات پیامی که به آن پاسخ داده شده"""
        if self.reply_to:
            return {
                'id': self.reply_to.id,
                'user': self.reply_to.created_by.get_full_name() or self.reply_to.created_by.username,
                'message_preview': self.reply_to.message[:50] + '...' if len(
                    self.reply_to.message) > 50 else self.reply_to.message,
            }
        return None

    def __str__(self):
        return f"Response #{self.id} for {self.ticket.tracking_code}"

class TicketNote(models.Model):
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name='notes')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='ticket_notes')
    content = models.TextField()
    is_private = models.BooleanField(default=False,  )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'TicketNote'
        verbose_name_plural = 'TicketNotes'
        db_table = 'Tickets-Notes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Note #{self.id} for {self.ticket.tracking_code}"

    def can_view(self, user):
        """بررسی آیا کاربر می‌تواند این یادداشت را ببیند"""
        if user.is_staff or user.is_superuser:
            return True
        if self.is_private:
            # فقط کارکنان می‌توانند یادداشت خصوصی را ببینند
            return user.groups.filter(name='کارکنان').exists()
        return True

    def can_user_edit(self, user):
        """بررسی آیا کاربر می‌تواند این یادداشت را ویرایش کند"""
        # فقط ایجادکننده اصلی می‌تواند ویرایش کند
        # حتی ادمین‌ها هم نمی‌توانند ویرایش کنند
        return user == self.created_by

    def can_user_delete(self, user):

        # فقط ایجادکننده اصلی می‌تواند حذف کند
        # حتی ادمین‌ها هم نمی‌توانند حذف کنند
        return user == self.created_by

    def can_user_view(self, user):
        """بررسی آیا کاربر می‌تواند این یادداشت را ببیند"""
        if user.is_staff or user.is_superuser:
            return True
        if self.is_private:
            # فقط کارکنان می‌توانند یادداشت خصوصی را ببینند
            return user.groups.filter(name='کارکنان').exists()
        return True

class AssignmentQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(assignee=user)

    def open(self):
        return self.filter(status_in=["new", "in_progress"])

class Assignment(TimestampedModel):
    assigned_ticket = models.ForeignKey(Ticket, related_name='assignments_tickets', on_delete=models.CASCADE,help_text="The ticket that will be assigned to this assignment")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assignments_users', on_delete=models.CASCADE,help_text="The user that will be assigned to this assignment")
    seen_at = models.DateTimeField(null=True, blank=True, help_text="The date the ticket was seen")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='new')
    description = models.TextField(blank=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='created_assignments')
    assigned_at = models.DateTimeField(auto_now_add=False, default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        db_table = 'Tickets-Assignments'
        constraints = [
            models.UniqueConstraint(fields=['assigned_ticket', 'assignee'], name='unique_ticket_assignee'),
        ]
        ordering = ['-created_at']

    def get_status_color(self):
        return STATUS_COLORS.get(self.status, '#6c757d')

    def __str__(self):
        return f"#{self.assigned_ticket.subject} assigned to {self.assignee.username}"

    def mark_as_seen(self, user=None):
        """علامت‌گذاری Assignment به عنوان دیده شده"""
        # فقط اگر Assignee اصلی باشد، seen_at را آپدیت می‌کند
        if not self.seen_at:
            self.seen_at = timezone.now()
            self.save(update_fields=['seen_at'])
            return True
        return False

    def is_seen(self):
        """بررسی آیا Assignment دیده شده است یا نه"""
        return self.seen_at is not None

    @property
    def seen_by_display(self):
        """نمایش نام کاربری که Assignment را دیده است"""
        if self.seen_at and self.assignee:
            return f"دیده شده توسط: {self.assignee.get_full_name() or self.assignee.username}"
        return "هنوز دیده نشده"

    objects = AssignmentQuerySet.as_manager()
    
class SearchLogSignal(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_logs')
    search_query = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    response_status = models.CharField(max_length=100, blank=True)
    search_mode = models.CharField(max_length=10, default='and')
    results_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'SearchLog'
        verbose_name_plural = 'SearchLogs'
        db_table = 'Tickets-SearchLogs'
        ordering = ['-created_at']

        permissions = [
            #codename(permission_name) , name
            ("search_log_export" , "Can export search logs"),
        ]


    def __str__(self):
        output = f" AT {self.created_at}"
        if self.user is not None:
            return output + f" By {self.user}"
        else:
            return output + " By Guest"

class Swiper(TimestampedModel):
    title = models.CharField(max_length=100, blank=True, null=True, default='title_swiper')
    name_swiper = models.CharField(max_length=100, blank=True, null=True)
    main_image = models.FileField(upload_to='swiper/', null=True, blank=True)
    name_of_alt = models.CharField(max_length=100, blank=True, null=True)
    description_swiper = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name_swiper

class TicketAttachment(TimestampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,related_name="ticket_attachments")
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/%d/',blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)
    original_filename = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_ticket_attachments'
    )

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        db_table = 'Tickets_TicketAttachments'

    def __str__(self):
        # return f"{self.ticket}"
        return f"Attachment for {self.ticket.tracking_code}"

    def save(self, *args, **kwargs):
        if not self.original_filename and self.file:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)

class TicketSeenHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='seen_history')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Tickets-SeenHistory'
        unique_together = ['ticket', 'user']
        ordering = ['-seen_at']
        verbose_name = 'Seen History'
        verbose_name_plural = 'Seen Histories'

    def __str__(self):
        return f"{self.user.username} saw ticket #{self.ticket.tracking_code} at {self.seen_at}"

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,related_name='activities')
    action = models.CharField(max_length=100,choices=ACTION_CHOICES)
    field = models.CharField(max_length=100,blank=True)
    # تغییر دادن از کم به زیاد مثلا
    old_value = models.CharField(max_length=100,blank=True)
    new_value = models.CharField(max_length=100,blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # اپدیت نداره چون رکورد این جدول فقط ثبت میشود و اپدیت نمیشود

    class Meta:
        verbose_name = 'ActivityLog'
        verbose_name_plural = 'ActivityLogs'
        db_table = 'Tickets-ActivityLogs'
        ordering = ['-created_at']

# class Role(models.Model):
#     title = models.CharField(max_length=100)  # English
#     persian_title = models.CharField(max_length=100)
#     level = models.IntegerField(default=0)  # سطح دسترسی (عدد کمتر = سطح بالاتر)
#     sort = models.PositiveIntegerField(default=0)
#
#     def __str__(self):
#         return f"{self.persian_title} ({self.title})"
#
#     class Meta:
#         verbose_name = 'Role'
#         verbose_name_plural = 'Roles'
#         db_table = 'Tickets-Roles'
#         ordering = ['level']
#
# class UserRole(TimestampedModel):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='user_roles',blank=True)
#     role = models.ForeignKey(Role, on_delete=models.CASCADE,blank=True)
#
#     def __str__(self):
#         return f"{self.user.username} role #{self.role.title}"
#
#     class Meta:
#         verbose_name = 'UserRole'
#         verbose_name_plural = 'UserRoles'
#         db_table = 'Tickets-UserRoles'
#         ordering = ['-created_at']

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , related_name='notifications')
    ticket = models.ForeignKey("Tickets.Ticket", on_delete=models.CASCADE,related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
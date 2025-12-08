from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify, capfirst
from django.utils.timezone import now
from .Choices import *
from django.contrib.auth.models import User


class TimestampedModel(models.Model):
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
    is_active = models.BooleanField(default=True)

    class Meta:
        # برای ادمین پنل دیگه S اضافه نگیره
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

        # برای دیتابیس
        db_table = 'Tickets-Categories'

    objects = CategoryQuerySet.as_manager()

    # def __str__(self):
    #     return capfirst(self.name)

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

# class Ticket(TimestampedModel):
#     category = models.ForeignKey(Category,related_name='tickets',on_delete=models.SET_NULL,null=True,blank=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='tickets',on_delete=models.PROTECT,default=None,blank=True)
#     priority = models.CharField(max_length=100, default="Low", choices=PRIORITY_CHOICES)
#     subject = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     tags = models.ManyToManyField(Tag, related_name='tickets', blank=True)
#     max_replay_date = models.DateTimeField(help_text="The maximum replay date the ticket will reply")
#     closed_at = models.DateTimeField(null=True, blank=True)
#     tracking_code = models.CharField(max_length=100, null=True, blank=True,unique=True)
#
#     class Meta:
#         verbose_name = 'Ticket'
#         verbose_name_plural = 'Tickets'
#
#         db_table = 'Tickets-Ticket'
#
#         indexes = [
#             models.Index(fields=['category']),
#             models.Index(fields=['priority']),
#         ]
#
#         ordering = ['-created_at']
#
#     def save(self, *args, **kwargs):
#         is_new = self.pk is None
#         super().save(*args, **kwargs) #save first to  get primary key
#         if is_new and not self.tracking_code:
#             self.tracking_code = f"TCK-{now().strftime('%Y%m%d')}-{self.pk:05d}"
#             # Example :TCK-20250913-00001
#             super().save(update_fields=['tracking_code'])
#
#
#     def get_priority_color(self):
#         return PRIORITY_COLORS.get(self.priority, '#6c757d')
#
#     def delete(self, *args, **kwargs):
#         #  جلوگیری از پاک شدن در سطح مدل
#         if self.priority == 'high':
#             raise PermissionDenied("Cannot delete tickets with HIGH priority")
#         super().delete(*args, **kwargs)
#
#     def __str__(self):
#         return f"#{self.tracking_code} {self.subject[:30]}..."

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
    category = models.ForeignKey(Category,related_name='tickets',on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='tickets',on_delete=models.PROTECT,default=None,blank=True)
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
        super().save(*args, **kwargs)
        if is_new and not self.tracking_code:
            self.tracking_code = f"TCK-{now().strftime('%Y%m%d')}-{self.pk:05d}"
            super().save(update_fields=['tracking_code'])

    def get_priority_color(self):
        return PRIORITY_COLORS.get(self.priority, '#6c757d')

    def get_status_color(self):
        return STATUS_COLORS.get(self.status, '#6c757d')

    def get_department_color(self):
        return DEPARTMENT_COLORS.get(self.department, '#6c757d')

    def get_edit_url(self):
        return reverse('tickets-update',args=[self.pk])

    def get_absolute_url(self):
        return  reverse('tickets-details',args=[self.pk])

    def get_delete_url(self):
        return reverse('tickets-destroy',args=[self.pk])

    def get_tickets_url(self):
        return reverse('tickets',args=[self.pk])

    def delete(self, *args, **kwargs):
        if self.priority == 'high':
            raise PermissionDenied("Cannot delete tickets with HIGH priority")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"#{self.tracking_code} {self.subject[:30]}..."

    objects = TicketQuerySet.as_manager()

class TicketResponse(TimestampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='responses')
    message = models.TextField()
    response_status = models.CharField(max_length=10, choices=RESPONSE_STATUS_CHOICES, default='sent')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Tickets-Responses'
        ordering = ['created_at']

    def get_response_status_color(self):
        return RESPONSE_STATUS_COLORS.get(self.response_status, '#6c757d')

    def __str__(self):
        return f"Response #{self.id} for {self.ticket.tracking_code}"

class Assignment(TimestampedModel):
    assigned_ticket = models.ForeignKey(Ticket,related_name='assignments_tickets',on_delete=models.CASCADE,help_text="The ticket that will be assigned to this assignment")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='assignments_users',on_delete=models.CASCADE,help_text="The user that will be assigned to this assignment")
    seen_at = models.DateTimeField(null=True, blank=True ,help_text="The date the ticket was seen")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='new')
    description = models.TextField(blank=True)

    # assigned_ticket ...........assignee
    # 100..............................1001
    # 100..............................1002
    # 100..............................1003
    # 100..............................1004
    # 100..............................1005
    # 107..............................1006

    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        db_table = 'Tickets-Assignments'

        constraints = [
            models.UniqueConstraint(fields=['assigned_ticket','assignee' ], name='unique_ticket_assignee'),
        ]
        ordering = ['-created_at']

    def get_status_color(self):
        return STATUS_COLORS.get(self.status , '#6c757d')

    # def __str__(self):
    #     # return f"#{self.pk} {self.assignee[:30]}..."
    #     return f"#{self.assigned_ticket.subject} assigned to {self.assignee.name}..."

    def __str__(self):
        # بهترین گزینه - استفاده از username
        return f"#{self.assigned_ticket.subject} assigned to {self.assignee.username}"

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

    # def __str__(self):
    #     return f"{self.user.username} searched: {self.search_query}"

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
 
# راه دوم برای ساخت logSearch

# class LogSearch(models.Model):
#     search_subject = models.CharField(max_length=200)
#     search_category = models.CharField(max_length=200)
#     search_priority = models.CharField(max_length=200)
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='search_user',
#         blank=True,
#         null=True,
#         default=None,
#         # editable=False
#     )
#
#     class Meta:
#         verbose_name = 'LogSearch'
#         verbose_name_plural = 'LogSearch'
#         db_table = 'Tickets-LogSearch'
#
#     def __str__(self):
#         output = f" AT {self.created_at}"
#         if self.user is not None:
#             return output + f" By {self.user}"
#         else:
#             return output + " By Guest"

class TicketAttachment(TimestampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,related_name="ticket_attachments")
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/%d/',blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)
    original_filename = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        db_table = 'Tickets_TicketAttachments'

    def __str__(self):
        return f"{self.ticket}"

    def save(self, *args, **kwargs):
        if not self.original_filename and self.file:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils.text import slugify, capfirst
from django.utils.timezone import now
from .Choices import *

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

class Category(NameSlugModel):
    is_active = models.BooleanField(default=True)

    class Meta:
        # برای ادمین پنل دیگه S اضافه نگیره
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

        # برای دیتابیس
        db_table = 'Tickets-Categories'

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

class Ticket(TimestampedModel):
    category = models.ForeignKey(Category,related_name='tickets',on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='tickets',on_delete=models.PROTECT,default=None,blank=True)
    priority = models.CharField(max_length=100, default="Low", choices=PRIORITY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name='tickets', blank=True)
    max_replay_date = models.DateTimeField(help_text="The maximum replay date the ticket will reply")
    closed_at = models.DateTimeField(null=True, blank=True)
    tracking_code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    contact_name = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, default="Django", choices=DEPARTMENT_CHOICES)
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

    def delete(self, *args, **kwargs):
        if self.priority == 'high':
            raise PermissionDenied("Cannot delete tickets with HIGH priority")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"#{self.tracking_code} {self.subject[:30]}..."

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

class TicketAttachment(TimestampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        db_table = 'Tickets-Attachments'
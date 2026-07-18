from django.contrib import admin , messages
from django.contrib.admin import ModelAdmin
from django.core.exceptions import PermissionDenied

from .models import *


@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):

    list_display = ['site_name','is_active','maintenance_mode','get_updated_by','updated_at',]

    list_filter = ['is_active','maintenance_mode','enable_notifications','default_language',]

    search_fields = ['site_name','tagline','meta_title','analytics_id',]

    readonly_fields = ['created_at','updated_at','get_updated_by',]

    exclude = ['updated_by']

    fieldsets = (
        ('🏷️ اطلاعات پایه سایت', {
            'fields': (
                'site_name',
                'tagline',
                'topbar',
                ('logo', 'favicon'),
            ),
            'classes': ('wide',),
        }),

        ('🔍 متا و سئو (SEO)', {
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
            ),
            'classes': ('collapse',),
        }),

        ('🌐 زبان و منطقه زمانی', {
            'fields': (
                ('default_language', 'timezone'),
            ),
        }),


        ('📱 شبکه‌های اجتماعی', {
            'fields': (
                'linkedin',
            ),
            'classes': ('collapse',),
        }),

        ('⚙️ تنظیمات عمومی', {
            'fields': (
                'analytics_id',
                ('maintenance_mode', 'enable_registration'),
                'enable_captcha',
                'items_per_page',
            ),
        }),

        ('🔒 تنظیمات امنیتی', {
            'fields': (
                'max_login_attempts',
                'session_timeout_minutes',
                'password_min_length',
            ),
            'classes': ('collapse',),
        }),

        ('📁 تنظیمات فایل', {
            'fields': (
                'max_file_size_mb',
                'allowed_file_types',
            ),
            'classes': ('collapse',),
        }),

        ('🎫 تنظیمات تیکت', {
            'fields': (
                ('ticket_auto_close_days', 'max_open_tickets_per_user'),
                ('default_ticket_priority', 'ticket_number_prefix'),
                ('allow_guest_tickets', 'ticket_auto_assign'),
                'enable_ticket_rating',
            ),
            'classes': ('wide',),
        }),

        ('🔔 تنظیمات نوتیفیکیشن', {
            'fields': (
                # فعال/غیرفعال کلی
                ('enable_notifications', 'log_all_notifications'),

                # کانال‌های ارسال
                ('enable_email_notifications', 'enable_push_notifications'),

                # رویدادها
                ('notify_on_new_ticket', 'notify_on_ticket_reply'),
                ('notify_on_ticket_assignment', 'notify_on_ticket_status_change'),
                ('notify_on_ticket_escalation', 'notify_on_ticket_deadline'),
                'notify_on_high_priority_only',

                # دریافت‌کنندگان
                ('notify_admin_on_new_ticket', 'notify_user_on_reply'),
                ('notify_agent_on_assignment', 'notify_all_admins'),

                # محدودیت‌ها
                ('notification_rate_limit_per_minute', 'notification_cooldown_minutes'),
                'max_notifications_per_day',

                # اولویت‌بندی
                ('default_notification_priority', 'high_priority_force_email'),
                'notification_retry_count',
            ),
            'classes': ('wide', 'collapse'),
        }),

        ('📊 اطلاعات مدیریتی', {
            'fields': (
                'is_active',
                'created_at',
                'updated_at',
                'get_updated_by',
            ),
            'classes': ('collapse',),
        }),
    )
    # ===== متد نمایش کاربر =====
    def get_updated_by(self, obj):
        """نمایش کاربر بروزرسانی‌کننده"""
        if obj.updated_by:
            return obj.updated_by.username
        return '—'

    get_updated_by.short_description = 'بروزرسانی شده توسط'

    # ===== ذخیره خودکار =====
    def save_model(self, request, obj, form, change):
        """ثبت خودکار کاربر بروزرسانی‌کننده"""
        obj.updated_by = request.user
        obj.save()

        self.message_user(
            request,
            f'✅ تنظیمات "{obj.site_name}" با موفقیت ذخیره شد.',
            messages.SUCCESS
        )

    # ===== محدودیت‌ها =====
    def has_add_permission(self, request):
        """فقط یک رکورد مجاز است"""
        if SiteSetting.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """آخرین رکورد قابل حذف نیست"""
        if obj and SiteSetting.objects.count() == 1:
            return False
        return super().has_delete_permission(request, obj)




# اجازه دسترسی به ادمین و سوپرادمین

    # def has_permission(self, request):
    #     """
    #     بررسی دسترسی کلی - فقط ادمین‌ها و سوپرادمین‌ها
    #     """
    #     # سوپرادمین همیشه دسترسی دارد
    #     if request.user.is_superuser:
    #         return True
    #
    #     # کاربران استاف (ادمین‌ها)
    #     if request.user.is_staff:
    #         # گروه‌های مجاز
    #         allowed_groups = [
    #             'Admin',
    #             'مدیران',
    #             'Support Manager',
    #             'مدیر پشتیبانی',
    #             'Super Admin',
    #             'ادمین'
    #         ]
    #
    #         # بررسی عضویت در گروه‌های مجاز
    #         user_groups = request.user.groups.values_list('name', flat=True)
    #         if any(group in allowed_groups for group in user_groups):
    #             return True
    #
    #         # یا اگر permission خاصی دارد
    #         if request.user.has_perm('settings.change_sitesetting'):
    #             return True
    #
    #     return False

    # def has_view_permission(self, request, obj=None):
    #     """اجازه مشاهده"""
    #     return self.has_permission(request)
    #
    # def has_add_permission(self, request):
    #     """اجازه افزودن - فقط سوپرادمین یا ادمین‌های خاص"""
    #     if request.user.is_superuser:
    #         return True
    #
    #     if request.user.is_staff and request.user.has_perm('settings.add_sitesetting'):
    #         return True
    #
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     """اجازه ویرایش - فقط سوپرادمین یا ادمین‌های خاص"""
    #     if request.user.is_superuser:
    #         return True
    #
    #     if request.user.is_staff and request.user.has_perm('settings.change_sitesetting'):
    #         return True
    #
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     """اجازه حذف - فقط سوپرادمین"""
    #     return request.user.is_superuser
    #
    # def get_queryset(self, request):
    #     """
    #     محدود کردن لیست نمایش (اختیاری)
    #     """
    #     qs = super().get_queryset(request)
    #
    #     # سوپرادمین همه رو می‌بینه
    #     if request.user.is_superuser:
    #         return qs
    #
    #     # ادمین‌ها فقط رکوردهای فعال رو می‌بینند
    #     if self.has_permission(request):
    #         return qs.filter(is_active=True)
    #
    #     # بقیه هیچی نبینند
    #     return qs.none()
    #
    # def save_model(self, request, obj, form, change):
    #     """ذخیره با بررسی دسترسی"""
    #     # بررسی دسترسی برای ویرایش
    #     if not self.has_change_permission(request):
    #         raise PermissionDenied("شما اجازه ویرایش تنظیمات را ندارید.")
    #
    #     obj.updated_by = request.user
    #     obj.save()
    #
    #     self.message_user(
    #         request,
    #         f'✅ تنظیمات "{obj.site_name}" با موفقیت ذخیره شد.',
    #         messages.SUCCESS
    #     )
    #
    # def delete_model(self, request, obj):
    #     """حذف با بررسی دسترسی"""
    #     if not self.has_delete_permission(request):
    #         raise PermissionDenied("شما اجازه حذف تنظیمات را ندارید.")
    #
    #     if SiteSetting.objects.count() == 1:
    #         self.message_user(
    #             request,
    #             '⚠️ شما نمی‌توانید آخرین رکورد تنظیمات را حذف کنید!',
    #             messages.ERROR
    #         )
    #         return
    #
    #     obj.delete()
    #     self.message_user(
    #         request,
    #         f'✅ تنظیمات "{obj.site_name}" با موفقیت حذف شد.',
    #         messages.SUCCESS
    #     )
    #
    # # ===== متدهای نمایش =====
    # def get_updated_by(self, obj):
    #     if obj.updated_by:
    #         return obj.updated_by.username
    #     return '—'
    #
    # get_updated_by.short_description = 'بروزرسانی شده توسط'



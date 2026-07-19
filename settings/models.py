from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models

from Tickets.Choices import PRIORITY_CHOICES
from settings.constants import SITE_SETTINGS_CACHE_KEY, SITE_SETTINGS_CACHE_TIMEOUT


class SiteSetting(models.Model):
    # ===== اطلاعات پایه سایت =====
    site_name = models.CharField(max_length=255, verbose_name='نام سایت')
    tagline = models.CharField(max_length=255, blank=True, verbose_name='شعار سایت')
    topbar = models.CharField(max_length=255, blank=True, verbose_name='متن نوار بالا')

    # ===== متا =====
    meta_title = models.CharField(max_length=255, blank=True, verbose_name='عنوان متا')
    meta_description = models.TextField(max_length=500, blank=True,verbose_name='توضیحات متا')
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name='کلمات کلیدی')
    # author = models.CharField(max_length=100, blank=True, verbose_name='نویسنده')

    # ===== لوگو و آیکون =====
    logo = models.ImageField(upload_to='settings/logo/', blank=True, null=True, verbose_name='لوگو')
    favicon = models.ImageField(upload_to='settings/favicon/', blank=True, null=True, verbose_name='آیکون مرورگر')

    # ===== تنظیمات زبان و زمان =====
    default_language = models.CharField(max_length=10,default='fa',choices=[('fa', 'فارسی'), ('en', 'انگلیسی')],verbose_name='زبان پیش‌فرض')
    timezone = models.CharField(max_length=50,default='Asia/Tehran',verbose_name='منطقه زمانی')

    # ===== شبکه‌های اجتماعی =====
    # facebook = models.URLField(blank=True, verbose_name='فیسبوک')
    # instagram = models.URLField(blank=True, verbose_name='اینستاگرام')
    # twitter = models.URLField(blank=True, verbose_name='توییتر')
    # whatsapp = models.URLField(blank=True, verbose_name='واتساپ')
    # telegram = models.URLField(blank=True, verbose_name='تلگرام')
    linkedin = models.URLField(blank=True, verbose_name='لینکدین')

    # ===== اطلاعات تماس =====
    # email = models.EmailField(blank=True, verbose_name='ایمیل اصلی')
    # phone = models.TextField(blank=True,verbose_name='تلفن‌ها',help_text='مثلاً: {"دفتر": "021-12345678", "موبایل": "09121234567"}')
    # address = models.TextField(blank=True,verbose_name='ادرس')
    # ===== آنالیتیکس =====
    analytics_id = models.CharField(max_length=255, blank=True, verbose_name='کد گوگل آنالیتیکس')
    maintenance_mode = models.BooleanField(default=False, verbose_name='حالت تعمیرات')
    enable_registration = models.BooleanField(default=True, verbose_name='فعال بودن ثبت نام')
    # enable_comments = models.BooleanField(default=True, verbose_name='فعال بودن کامنت')
    # ===== تنظیمات ظاهری =====
    items_per_page = models.PositiveIntegerField(default=20, verbose_name='تعداد آیتم در هر صفحه')
    enable_captcha = models.BooleanField(default=True, verbose_name='فعال بودن کپچا')
    # primary_color = models.CharField(max_length=20, default='#0d6efd', verbose_name='رنگ اصلی سایت')

    # ===== تنظیمات امنیتی =====
    max_login_attempts = models.PositiveIntegerField(default=5, verbose_name='حداکثر تلاش برای ورود')
    session_timeout_minutes = models.PositiveIntegerField(default=60, verbose_name='زمان انقضای نشست')
    password_min_length = models.PositiveIntegerField(default=8, verbose_name='حداقل طول رمز عبور')

    # ===== تنظیمات فایل =====
    max_file_size_mb = models.PositiveIntegerField(default=5, verbose_name='حداکثر حجم فایل (مگابایت)')
    allowed_file_types = models.TextField(default='jpg,jpeg,png,pdf,zip,doc,docx',verbose_name='پسوندهای مجاز',help_text='با کاما جدا کنید')

    # ===== تنظیمات تیکت =====
    ticket_auto_close_days = models.PositiveIntegerField(default=7,verbose_name='روز تا بسته شدن خودکار تیکت')
    max_open_tickets_per_user = models.PositiveIntegerField(default=5,verbose_name='حداکثر تیکت باز برای هر کاربر')
    default_ticket_priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES,default='middle',verbose_name='اولویت پیش‌فرض تیکت')
    allow_guest_tickets = models.BooleanField(default=True, verbose_name='اجازه تیکت مهمان')
    ticket_number_prefix = models.CharField(max_length=20, default='TKT-', verbose_name='پیشوند شماره تیکت')
    ticket_auto_assign = models.BooleanField(default=False, verbose_name='اختصاص خودکار تیکت')
    enable_ticket_rating = models.BooleanField(default=True, verbose_name='امتیازدهی به تیکت')

    # ===== تنظیمات ایمیل =====
    # smtp_host = models.CharField(max_length=255, blank=True, verbose_name='سرور SMTP')
    # smtp_port = models.PositiveIntegerField(default=587, verbose_name='پورت SMTP')
    # smtp_username = models.CharField(max_length=255, blank=True, verbose_name='نام کاربری SMTP')
    # smtp_password = models.CharField(max_length=255, blank=True, verbose_name='رمز عبور SMTP')
    # use_tls = models.BooleanField(default=True, verbose_name='استفاده از TLS')

    # ===== تنظیمات پیامک =====
    # sms_api_key = models.CharField(max_length=255, blank=True, verbose_name='کلید API پیامک')
    # sms_sender_number = models.CharField(max_length=20, blank=True, verbose_name='شماره فرستنده')
    # sms_enabled = models.BooleanField(default=False, verbose_name='فعال بودن پیامک')

    # ----- فعال/غیرفعال کردن کلی -----
    enable_notifications = models.BooleanField(default=True,verbose_name='فعال بودن سیستم نوتیفیکیشن')

    # ----- کانال‌های ارسال -----
    enable_email_notifications = models.BooleanField(default=True,verbose_name='ارسال نوتیفیکیشن از طریق ایمیل')
    # enable_sms_notifications = models.BooleanField(default=False,verbose_name='ارسال نوتیفیکیشن از طریق پیامک')
    enable_push_notifications = models.BooleanField(default=True,verbose_name='ارسال نوتیفیکیشن درون برنامه‌ای (Push)')
    # enable_telegram_notifications = models.BooleanField(default=False,verbose_name='ارسال نوتیفیکیشن از طریق تلگرام')

    # ----- رویدادهای نوتیفیکیشن -----
    notify_on_new_ticket = models.BooleanField(default=True,verbose_name='ارسال برای تیکت جدید')
    notify_on_ticket_reply = models.BooleanField(default=True,verbose_name='ارسال برای پاسخ جدید به تیکت')
    notify_on_ticket_assignment = models.BooleanField(default=True,verbose_name='ارسال برای اختصاص تیکت')
    notify_on_ticket_status_change = models.BooleanField(default=True,verbose_name='ارسال برای تغییر وضعیت تیکت')
    notify_on_ticket_escalation = models.BooleanField(default=True,verbose_name='ارسال برای افزایش اولویت تیکت')
    notify_on_ticket_deadline = models.BooleanField(default=True,verbose_name='ارسال برای نزدیک شدن به مهلت تیکت')
    notify_on_high_priority_only = models.BooleanField(default=False,verbose_name='فقط برای تیکت‌های با اولویت بالا ارسال شود')

    # ----- دریافت ‌کنندگان نوتیفیکیشن -----
    notify_admin_on_new_ticket = models.BooleanField(default=True,verbose_name='ارسال به ادمین‌ها برای تیکت جدید')
    notify_user_on_reply = models.BooleanField(default=True,verbose_name='ارسال به کاربر برای پاسخ جدید')
    notify_agent_on_assignment = models.BooleanField(default=True,verbose_name='ارسال به پشتیبان برای تیکت جدید')
    notify_all_admins = models.BooleanField(default=False,verbose_name='ارسال به تمام ادمین‌ها (نه فقط ادمین تیکت)')

    # ----- تنظیمات ایمیل -----
    # email_from_address = models.EmailField(default='noreply@yourdomain.com',verbose_name='آدرس فرستنده ایمیل')
    # email_reply_to = models.EmailField(blank=True,null=True,verbose_name='آدرس پاسخ به ایمیل')
    # email_cc_list = models.TextField(blank=True,verbose_name='لیست CC ایمیل‌ها',help_text='ایمیل‌ها را با کاما جدا کنید')
    # email_bcc_list = models.TextField(blank=True,verbose_name='لیست BCC ایمیل‌ها',help_text='ایمیل‌ها را با کاما جدا کنید')

    # ----- تنظیمات پیامک -----
    # SMS_PROVIDERS = [('kavenegar', 'کاوه‌نگار'),('melipayamak', 'ملی پیامک'),('farapayamak', 'فراپیامک'),('raygan', 'رایگان'),]
    # sms_provider = models.CharField(max_length=50,choices=SMS_PROVIDERS,default='kavenegar',verbose_name='ارائه‌دهنده پیامک')
    # sms_api_key = models.CharField(max_length=255,blank=True,verbose_name='کلید API پیامک')
    # sms_sender_number = models.CharField(max_length=20,blank=True,verbose_name='شماره فرستنده پیامک')
    # sms_template = models.CharField(max_length=500,blank=True,verbose_name='قالب پیامک',help_text='متغیرها: {name}, {ticket_id}, {title}, {url}')

    # ----- تنظیمات تلگرام -----
    # telegram_bot_token = models.CharField(max_length=255,blank=True,verbose_name='توکن ربات تلگرام')
    # telegram_chat_id = models.CharField(max_length=50,blank=True,verbose_name='Chat ID کانال/گروه تلگرام')
    # telegram_enable_for_users = models.BooleanField(default=False,verbose_name='اجازه ارسال تلگرام به کاربران (با ثبت chat_id)')

    # ----- محدودیت‌ها و زمان‌بندی -----
    notification_rate_limit_per_minute = models.PositiveIntegerField(default=10,verbose_name='حداکثر نوتیفیکیشن در دقیقه')
    notification_cooldown_minutes = models.PositiveIntegerField(default=5,verbose_name='فاصله زمانی بین نوتیفیکیشن‌های تکراری (دقیقه)')
    max_notifications_per_day = models.PositiveIntegerField(default=100,verbose_name='حداکثر نوتیفیکیشن در روز برای هر کاربر')

    # ----- اولویت‌بندی -----
    NOTIFICATION_PRIORITY_CHOICES = [('HIGH', 'بالا'),('MEDIUM', 'متوسط'),('LOW', 'کم'),]
    default_notification_priority = models.CharField(max_length=10,choices=NOTIFICATION_PRIORITY_CHOICES,default='MEDIUM',verbose_name='اولویت پیش‌فرض نوتیفیکیشن')
    high_priority_force_email = models.BooleanField(default=True,verbose_name='ارسال حتمی ایمیل برای نوتیفیکیشن‌های با اولویت بالا')

    # ----- لاگ نوتیفیکیشن -----
    log_all_notifications = models.BooleanField(default=True,verbose_name='ثبت لاگ تمام نوتیفیکیشن‌ها')
    notification_retry_count = models.PositiveIntegerField(default=3,verbose_name='تعداد تلاش مجدد برای ارسال ناموفق')

    # ===== فیلدهای مدیریتی =====
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='settings_tickets', on_delete=models.SET_NULL,null=True, blank=True, default=None,editable=False, verbose_name='بروزرسانی شده توسط')

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
        db_table = "Tickets_site_setting"


    def save(self, *args, **kwargs):
        # فقط یک رکورد مجاز است
        if not self.pk and SiteSetting.objects.exists():
            raise ValidationError("Only one SiteSetting instance is allowed")

        # اعتبارسنجی
        self.full_clean()

        super().save(*args, **kwargs)

        # پاک کردن کش
        cache.delete(SITE_SETTINGS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        cache.delete(SITE_SETTINGS_CACHE_KEY)


        super().delete(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """
        دریافت تنظیمات فعال (با کش)
        """
        # ===== مرحله 1: از کش بخون =====
        settings = cache.get(SITE_SETTINGS_CACHE_KEY)

        # ===== مرحله 2: اگه تو کش نبود =====
        if settings is None:
            try:
                # از دیتابیس بگیر
                settings = cls.objects.filter(is_active=True).first()

                # اگه پیدا شد، تو کش ذخیره کن
                if settings:
                    cache.set(
                        SITE_SETTINGS_CACHE_KEY,
                        settings,
                        SITE_SETTINGS_CACHE_TIMEOUT
                    )
                    print(f"✅ Settings loaded from DB and cached: {settings.site_name}")
                else:
                    # اگه هیچ تنظیماتی وجود نداره
                    print("⚠️ No settings found in database")
                    # یه None تو کش ذخیره کن تا دوباره دیتابیس نزنه
                    cache.set(SITE_SETTINGS_CACHE_KEY, None, 60)  # ۱ دقیقه

            except Exception as e:
                print(f"❌ Error loading settings: {e}")
                settings = None

        return settings



    @classmethod
    def get_setting_value(cls, field_name, default=None):
        """
        دریافت مقدار یک فیلد خاص از تنظیمات
        مثال: SiteSetting.get_setting_value('site_name', 'سایت من')
        """
        settings = cls.get_settings()
        if settings:
            return getattr(settings, field_name, default)
        return default

    @classmethod
    def clear_cache(cls):
        """پاک کردن کش تنظیمات"""
        cache.delete(SITE_SETTINGS_CACHE_KEY)


    # فقط وقتی در صفحه services.py فعال کردی این جا فعال شود
    # @classmethod
    # def get_default(cls):
    #     """ایجاد و برگرداندن تنظیمات پیش‌فرض"""
    #     defaults = {
    #         'site_name': 'سایت من',
    #         'tagline': 'زیرنویس سایت',
    #         'topbar': 'متن نوار بالا',
    #         'meta_title': 'عنوان سایت',
    #         'meta_description': 'توضیحات متا',
    #         'default_language': 'fa',
    #         'timezone': 'Asia/Tehran',
    #         'maintenance_mode': False,
    #         'enable_registration': True,
    #         'items_per_page': 20,
    #         'enable_captcha': True,
    #         'max_login_attempts': 5,
    #         'session_timeout_minutes': 60,
    #         'password_min_length': 8,
    #         'max_file_size_mb': 5,
    #         'allowed_file_types': 'jpg,jpeg,png,pdf,zip,doc,docx',
    #         'ticket_auto_close_days': 7,
    #         'max_open_tickets_per_user': 5,
    #         'default_ticket_priority': 'middle',
    #         'allow_guest_tickets': True,
    #         'ticket_number_prefix': 'TKT-',
    #         'ticket_auto_assign': False,
    #         'enable_ticket_rating': True,
    #         'enable_notifications': True,
    #         'enable_email_notifications': True,
    #         'enable_push_notifications': True,
    #         'notify_on_new_ticket': True,
    #         'notify_on_ticket_reply': True,
    #         'notify_on_ticket_assignment': True,
    #         'notify_on_ticket_status_change': True,
    #         'notify_on_ticket_escalation': True,
    #         'notify_on_ticket_deadline': True,
    #         'notify_on_high_priority_only': False,
    #         'notify_admin_on_new_ticket': True,
    #         'notify_user_on_reply': True,
    #         'notify_agent_on_assignment': True,
    #         'notify_all_admins': False,
    #         'notification_rate_limit_per_minute': 10,
    #         'notification_cooldown_minutes': 5,
    #         'max_notifications_per_day': 100,
    #         'default_notification_priority': 'MEDIUM',
    #         'high_priority_force_email': True,
    #         'log_all_notifications': True,
    #         'notification_retry_count': 3,
    #         'is_active': True,
    #     }
    #
    #     # ایجاد یک نمونه جدید با مقادیر پیش‌فرض
    #     setting = cls(**defaults)
    #     setting.save()
    #     return setting



    # def save(self, *args, **kwargs):
    #     if not self.pk and SiteSetting.objects.exists():
    #         raise ValidationError("فقط یک رکورد برای تنظیمات سایت مجاز است")
    #     super().save(*args, **kwargs)
    #
    #     cache.delete(SITE_SETTINGS_CACHE_KEY)

    # def delete(self, *args, **kwargs):
    #     cache.delete(SITE_SETTINGS_CACHE_KEY)
    #
    #     super().save(*args, **kwargs)


    # @classmethod
    # def get_settings(cls):
    #     """دریافت تنظیمات فعال"""
    #     return cls.objects.filter(is_active=True).first()

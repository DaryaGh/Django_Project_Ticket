# # from django.core.cache import cache
# # from django.core.management import BaseCommand
# #
# # from settings.constants import *
# # from settings.models import SiteSetting
# #
# #
# # class Command(BaseCommand):
# #     help = 'Initialization Site Settings'
# #
# #     def handle(self, *args, **options):
# #         if not SiteSetting.objects.exists():
# #             SiteSetting.objects.create(
# #                 site_name='Ticketing',
# #                 meta_description='This is my Awsome website !',
# #             )
# #
# #             settings = SiteSetting.objects.first()
# #
# #             cache.set(
# #                 SITE_SETTINGS_CACHE_KEY,
# #                 settings,
# #                 SITE_SETTINGS_CACHE_TIMEOUT
# #             )
# #
# #             self.stdout.write(self.style.SUCCESS('Site Settings Created Successfully'))
# #         else:
# #             self.stdout.write(self.style.WARNING('Site Settings Already Exists'))
#
#
# from django.core.cache import cache
# from django.core.management import BaseCommand
# from django.db import transaction
#
# from settings.constants import *
# from settings.models import SiteSetting
#
#
# class Command(BaseCommand):
#     help = 'Initialization Site Settings'
#
#     def handle(self, *args, **options):
#         try:
#             with transaction.atomic():
#                 # استفاده از get_or_create برای جلوگیری از ایجاد دوباره
#                 setting, created = SiteSetting.objects.get_or_create(
#                     id=1,  # یا هر شناسه یکتای دیگر
#                     defaults={
#                         'site_name': 'Ticketing258',
#                         'meta_description': 'This is my Awesome website !',
#                         'meta_keywords': ' Awesome website !',
#                     }
#                 )
#
#                 if created:
#                     # ذخیره در کش
#                     cache.set(
#                         SITE_SETTINGS_CACHE_KEY,
#                         setting,
#                         SITE_SETTINGS_CACHE_TIMEOUT
#                     )
#
#                     self.stdout.write(
#                         self.style.SUCCESS('Site Settings Created Successfully')
#                     )
#                 else:
#                     self.stdout.write(
#                         self.style.WARNING('Site Settings Already Exists')
#                     )
#
#         except Exception as e:
#             self.stdout.write(
#                 self.style.ERROR(f'Error creating site settings: {str(e)}')
#             )


from django.core.cache import cache
from django.core.management import BaseCommand
from django.db import transaction

from settings.constants import SITE_SETTINGS_CACHE_KEY, SITE_SETTINGS_CACHE_TIMEOUT
from settings.models import SiteSetting


class Command(BaseCommand):
    help = 'Initialization Site Settings'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # ===== مرحله 1: پاک کردن کش =====
                cache.delete(SITE_SETTINGS_CACHE_KEY)
                self.stdout.write('🗑️ Cache cleared')

                # ===== مرحله 2: حذف همه رکوردهای قبلی =====
                SiteSetting.objects.all().delete()
                self.stdout.write('🗑️ Old settings deleted')

                # ===== مرحله 3: ایجاد رکورد جدید =====
                setting = SiteSetting.objects.create(
                    site_name='Ticketing28',
                    meta_description='This is my Awesome website !',
                    meta_keywords='Awesome website !',
                    # فیلدهای دیگه رو هم میتونی مقداردهی کنی
                    is_active=True,
                    default_language='fa',
                    timezone='Asia/Tehran',
                    items_per_page=20,
                    max_login_attempts=5,
                    session_timeout_minutes=60,
                    password_min_length=8,
                    max_file_size_mb=5,
                    allowed_file_types='jpg,jpeg,png,pdf,zip,doc,docx',
                    ticket_auto_close_days=7,
                    max_open_tickets_per_user=5,
                    default_ticket_priority='middle',
                    allow_guest_tickets=True,
                    ticket_number_prefix='TKT-',
                    ticket_auto_assign=False,
                    enable_ticket_rating=True,
                )

                # ===== مرحله 4: ذخیره در کش =====
                cache.set(
                    SITE_SETTINGS_CACHE_KEY,
                    setting,
                    SITE_SETTINGS_CACHE_TIMEOUT
                )

                # ===== مرحله 5: تایید نهایی =====
                # چک کن که توی کش ذخیره شده
                cached = cache.get(SITE_SETTINGS_CACHE_KEY)
                if cached:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Site Settings Created Successfully')
                    )
                    self.stdout.write(f'   Site Name: {cached.site_name}')
                    self.stdout.write(f'   Cache Key: {SITE_SETTINGS_CACHE_KEY}')
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Failed to save to cache')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
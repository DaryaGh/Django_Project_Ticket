# from django.core.cache import cache
# from django.core.management import BaseCommand
#
# from settings.constants import *
# from settings.models import SiteSetting
#
#
# class Command(BaseCommand):
#     help = 'Initialization Site Settings'
#
#     def handle(self, *args, **options):
#         if not SiteSetting.objects.exists():
#             SiteSetting.objects.create(
#                 site_name='Ticketing',
#                 meta_description='This is my Awsome website !',
#             )
#
#             settings = SiteSetting.objects.first()
#
#             cache.set(
#                 SITE_SETTINGS_CACHE_KEY,
#                 settings,
#                 SITE_SETTINGS_CACHE_TIMEOUT
#             )
#
#             self.stdout.write(self.style.SUCCESS('Site Settings Created Successfully'))
#         else:
#             self.stdout.write(self.style.WARNING('Site Settings Already Exists'))


from django.core.cache import cache
from django.core.management import BaseCommand
from django.db import transaction

from settings.constants import *
from settings.models import SiteSetting


class Command(BaseCommand):
    help = 'Initialization Site Settings'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # استفاده از get_or_create برای جلوگیری از ایجاد دوباره
                setting, created = SiteSetting.objects.get_or_create(
                    id=1,  # یا هر شناسه یکتای دیگر
                    defaults={
                        'site_name': 'Ticketing258',
                        'meta_description': 'This is my Awesome website !',
                        'meta_keywords': ' Awesome website !',
                    }
                )

                if created:
                    # ذخیره در کش
                    cache.set(
                        SITE_SETTINGS_CACHE_KEY,
                        setting,
                        SITE_SETTINGS_CACHE_TIMEOUT
                    )

                    self.stdout.write(
                        self.style.SUCCESS('Site Settings Created Successfully')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Site Settings Already Exists')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating site settings: {str(e)}')
            )
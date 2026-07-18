from .constants import *
from .models import *

class SiteService:
    @staticmethod
    def settings():
        # check cache
        settings = cache.get(SITE_SETTINGS_CACHE_KEY)

        if settings is None:
            # fetch from DB
            # چک کنید که آیا اصلاً تنظیماتی وجود دارد یا نه
            settings = SiteSetting.objects.first()

            # if settings is None:
            #     # یا یک تنظیمات پیش‌فرض بسازید، یا یک استثنا پرتاب کنید
            #     settings = SiteSetting.get_default()

            if settings is None:
                # یا خطا بدهید
                raise ValueError("No site settings found. Please create one in admin panel.")

            cache.set(
                SITE_SETTINGS_CACHE_KEY,
                settings,
                SITE_SETTINGS_CACHE_TIMEOUT
            )

        return settings


# class SiteService:
#     @staticmethod
#     def settings():
#         settings = cache.get(SITE_SETTINGS_CACHE_KEY)
#
#         if settings is None:
#
#             settings = SiteSetting.objects.first()
#
#             cache.set(
#                 SITE_SETTINGS_CACHE_KEY,
#                 settings,
#                 SITE_SETTINGS_CACHE_TIMEOUT
#             )
#
#         return settings



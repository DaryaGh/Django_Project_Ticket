from pathlib import Path
from django.conf import settings
from django.conf.urls import static
from django.contrib import staticfiles
from dotenv import load_dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
DEBUG = os.getenv('DEBUG') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0v(5+x%h!5c_g%6apkbx)7=sak-6k@q-x7qvfeg5-*v5c$jbz5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    # 'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 'widget_tweaks'
    'Tickets',
    'settings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Tickets.middleware.CurrentUserMiddleware',
]

ROOT_URLCONF = 'Ticketing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'settings.context_processors.site_settings'

            ],
        },
    },
]

WSGI_APPLICATION = 'Ticketing.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'site-settings-cache',
    }
}

LOGIN_URL = '/Account/login/'  # آدرس صفحه لاگین شما
LOGIN_REDIRECT_URL = '/'  # آدرس بعد از لاگین موفق


# settings.py
# from pathlib import Path
# import os
#
# BASE_DIR = Path(__file__).resolve().parent.parent

from django.utils.translation import gettext_lazy as _

# اگر می‌خواهید CSS جداگانه برای RTL داشته باشید
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGES = [
    ('en', 'English'),
    ('fa', 'Persian'),
]

LANGUAGE_CODE = 'en'  # زبان پیش‌فرض
USE_I18N = True
USE_L10N = True






# # تنظیمات زبان

#
#
#
# LANGUAGE_CODE = 'fa'
#
# USE_I18N = True
# USE_L10N = True
# USE_TZ = True
#
# LANGUAGE_COOKIE_NAME = 'django_language'
# LANGUAGE_COOKIE_AGE = None
# LANGUAGE_COOKIE_PATH = '/'
#
# # زبان‌های فعال
# LANGUAGES = [
#     ('en', _('English')),
#     ('fa', _('Persian')),
# ]
#
# # مسیر فایل‌های ترجمه
# LOCALE_PATHS = [
#     # BASE_DIR / 'locale',
#     BASE_DIR / 'locale/',
# ]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/



TIME_ZONE = 'Asia/Tehran'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = 'static/'

# settings.py
import os

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

MEDIA_URL = '/media/'  # URL prefix for media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
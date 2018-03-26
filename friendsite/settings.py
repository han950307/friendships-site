"""
Django settings for friendsite project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import friendsite

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRIENDSHIP_VERSION = "0.0.2"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7@r-lqamj-2=za3b1lp+#d#fr)u4705e!)2azohsg=q1#@+7#_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# WSGI_APPLICATION = "friendsite.wsgi.application"
ALLOWED_HOSTS = ["18.188.123.79", "friendships.us", "www.friendships.us", "127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    'friendship.apps.FriendshipConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_crontab',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'friendsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'friendsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'friendship',
        'USER': 'root',
        'PASSWORD': 'friend',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'friendships',
    #     'USER': 'root',
    #     'PASSWORD': 'togetheragain',
    #     'HOST': '13.58.205.194',
    #     'PORT': '5432',
    # }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

CRONJOBS = [
    ('*/1 * * * *', 'friendship.cron.order_bid_update'),
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = 'friendship/static/friendship/'
STATIC_URL = '/static/'
MEDIA_ROOT = 'friendship/media/friendship/'
MEDIA_URL = '/media/'

EMAIL_HOST = '23.21.52.192'
EMAIL_HOST_USER = 'AKIAJGV6EBDOMNUSNNXA'
EMAIL_HOST_PASSWORD = 'AhrS5tvKP2jX7yb+Fmsl7CZOu2zACLj+ZnrLgoDZZRE/'
EMAIL_USE_TLS = True

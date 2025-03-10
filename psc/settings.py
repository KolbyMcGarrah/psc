"""
Django settings for psc project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dj_database_url
import dotenv
import django_heroku
from django.core.wsgi import get_wsgi_application

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Load environment variables from .env if it exists
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k@ssz-b+x*2s3l%w)q1_!)*$g2@1eaa(4a3kq$hc)y^w)(a&$1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['amadtest2.herokuapp.com', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'passlib',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'braintree',
    'stripe',
    'users',
    'pages',
    'tournament',
    'accounts',
    'pga_events',
    'credits',
]

AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'psc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psc.settings')


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
#Dev sqlite Database
#DATABASES = {
##        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}
#PostgreSQL Dev Database Configs
#DATABASES = {
#        'default':{
#            'ENGINE': 'django.db.backends.postgresql',
#            'NAME': 'amateuradvantage',
#            'USER': 'amad',
#            'PASSWORD': '#HangL00s3',
#            'HOST': 'localhost',
#            'PORT': '',
#        }
#}
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600)
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

DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m-%d-%Y'
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'MST'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/


#PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
#Dev static file settings
#STATIC_ROOT = ''
#STATIC_URL = '/static/'
#STATICFILES_DIRS = (os.path.join('static'),)

#HEROKU STATIC FILE settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join('static'),)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

BRAINTREE_MERCHANT_ID = 'pzbgb75kgpmvvj46'
BRAINTREE_PUBLIC_KEY = 'f423zx7536787s3f'
BRAINTREE_PRIVATE_KEY = 'af7353c37fb023f96ea98799c87caaf6'

#Use Test Stripe Keys
STRIPE_PUBLISHABLE_KEY = 'pk_test_y3aNGnrrQwW3InrwTnYfVNv100lSVzr9is'
STRIPE_SECRET_KEY = 'sk_test_g3KOhgnD0bGjNSao09orZdjG004zrMC2NR'
STRIPE_CLIENT_ID = 'ca_FPXmhPuP9iXwzPmCuZRuj3EN3FFMHx7C'
STRIPE_REDIRECT = f'https://amadtest2.herokuapp.com/credits/stripeConfirm'
#Set up emailing for Development. Will output to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


#EMAIL TEST. Will send to actual emails
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'kolbymcgarrah@gmail.com'
#EMAIL_USE_TLS = True
#Enter your gmail PW from the ADMINS email entered above.
#EMAIL_HOST_PASSWORD = '@Kbourne9'
#EMAIL_PORT = 587
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

django_heroku.settings(locals())
del DATABASES['default']['OPTIONS']['sslmode']
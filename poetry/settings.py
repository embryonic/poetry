"""
Django settings for poetry project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3@#m-+t6-o@#&jd4^(waj9m=$lrs8d4r!zqy*e))l*(dxtsymy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
     ('Chhota Ladka','chhotaladka02@gmail.com')
)

MANAGERS = ADMINS

SITE_ID = 1

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
#ALLOWED_HOSTS = ['sitename.com']


ALLOWED_HOSTS = []

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Application definition

INSTALLED_APPS = (
    # Default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Added 
    'formtools',
    'django.contrib.humanize',
    # pip installed
    'django_select2',
    'crispy_forms',
    'taggit',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',    
    # Developed by us
    'crawlers',
    'meta_tags',
    'common',
    'repository',
    'feedback',
    'dashboard',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'poetry.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [                
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                'django.template.context_processors.request',
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                'django.core.context_processors.csrf',
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",               
                'common.context_processors.getvars',
            ],
        },
    },
]

# Allauth related
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)
LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email',],
        'METHOD': 'js_sdk'  # instead of 'oauth2'
    }
}
ACCOUNT_SESSION_REMEMBER = None
# Allauth end

WSGI_APPLICATION = 'poetry.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default':
        {'ENGINE': 'django.db.backends.mysql', 'NAME': 'poetry3', 'HOST': '127.0.0.1', 'USER': 'root', 'PASSWORD': 'root', 'PORT': '3306'}
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Kolkata'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
#uncommnet for apache STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')
#STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'), #comment for apache
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# # CKeditor related
# CKEDITOR_JQUERY_URL = STATIC_URL + 'js/jquery-2.1.4.min.js'
# CKEDITOR_UPLOAD_PATH = 'images/'
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'Full',
#         'justifyClasses': [ 'AlignLeft', 'AlignCenter', 'AlignRight', 'AlignJustify' ],
#     },
#     
#     'config_text': {
#         'toolbar': 'Basic',        
#     },
# }

# django_select2 related
AUTO_RENDER_SELECT2_STATICS = True
# 
# Reference: 
# http://django-select2.readthedocs.org/en/latest/get_started.html#select2-bootstrap-default-false
SELECT2_BOOTSTRAP = True

# django-taggit related
# To make django-taggit to be CASE INSENSITIVE when looking up existing tags (by default False)
TAGGIT_CASE_INSENSITIVE = True

#
# Meta data
META_SITE_PROTOCOL = 'http'
META_SITE_DOMAIN = 'sitename.com' #using META_USE_SITE SETTING
META_SITE_TYPE = 'article' # override when passed in __init__
META_SITE_NAME = 'Site Name' #TODO
#META_INCLUDE_KEYWORDS = [] # keyword will be included in every article
#META_DEFAULT_KEYWORDS = [] # default when no keyword is provided in __init__
#META_IMAGE_URL = '' # Use STATIC_URL 
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_GOOGLEPLUS_PROPERTIES = True
META_USE_SITES = False #TODO check
META_PUBLISHER_FB_ID = 'https://www.facebook.com/SiteName' #TODO can use PAGE URL or Publisher id ID
META_PUBLISHER_GOOGLE_ID = 'https://plus.google.com/111112222333344444' #TODO Google+ ID 
META_FB_APP_ID = '' #TODO
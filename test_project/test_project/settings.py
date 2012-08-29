# Django settings for test_project project.
import os
import socket
import re

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

HOST_NAME = socket.gethostname()

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Test Admin', 'testadmin@fusionbox.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sqlite_database',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Denver'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# User-uploaded files
MEDIA_ROOT = os.path.join(PROJECT_PATH, '..', 'media')
MEDIA_URL = '/media/'

# Static files
STATIC_ROOT = os.path.join(PROJECT_PATH, '..', "static")
STATIC_URL = '/static/'
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'public'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'goc1b+$6epj8-i4@*vj7du2xud)3t!mw%r06a!n)4ke=ln96%b'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'fusionbox.error_logging.middleware.FusionboxCommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
  # 'fusionbox.middleware.GenericTemplateFinderMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
)

ROOT_URLCONF = 'test_project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'test_project.wsgi.application'

TEMPLATE_DIRS = (
        os.path.join(PROJECT_PATH, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    'debug_toolbar',
    'compressor',
    'fusionbox',
    'south',
    'django_extensions',
    'djangosecure',

    # Apps to be tested
    'fusionbox.error_logging',
    'test_app',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#SEND_BROKEN_LINK_EMAILS = True
# Use django-fusionbox error reporting
FUSIONBOX_SEND_BROKEN_LINK_EMAILS = True

# SEND EMAILS TO FILE BACKEND
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'tmp/email-messages/'

SCSS_IMPORTS = (
        STATICFILES_DIRS[0] + '/css',
        )

COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-sass', 'sass {infile} {outfile}'),

    # requires pyScss
    ('text/x-scss', 'pyscss {infile} -o {outfile} %s' %
      '-I ' + ' '.join(['"%s"' % d for d in SCSS_IMPORTS])
      )
)


FORCE_SCRIPT_NAME = ''

# <https://www.owasp.org/index.php/HTTPOnly#Browsers_Supporting_HttpOnly>
SESSION_COOKIE_HTTPONLY = True

# #Require ssl
# SECURE_SSL_REDIRECT = True
# #These must be set to True if SSL is in use
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Debug Toolbar Settings
INTERNAL_IPS = (
        '127.0.0.1',
        '63.228.88.83',
        '209.181.77.56',
        )

EMAIL_LAYOUT = 'mail/base.html'

IGNORABLE_404_URLS = (
        re.compile(r'\.(php|cgi)$'),
        re.compile(r'/null/?$'),  # This could be being caused by us.  Investigate?
        re.compile(r'^/phpmyadmin/', re.IGNORECASE),
        re.compile(r'^/wp-admin/'),
        re.compile(r'^/cgi-bin/'),
        re.compile(r'^(?!/static/).*\.(css|js)/?$'),
        )

# Import server specific settings 'settings_<hostname>.py'
try:
    import imp, sys
    module_name = 'settings_' + HOST_NAME
    module_info = imp.find_module(module_name, [PROJECT_PATH] + sys.path)
    live_settings = imp.load_module(module_name, *module_info)
except ImportError:
    pass
else:
    try:
        attrlist = live_settings.__all__
    except AttributeError:
        attrlist = dir (live_settings)
    for attr in attrlist:
        if attr.startswith('__'):
            continue
        globals()[attr] = getattr (live_settings, attr)

try:
    from settings_local import *
except ImportError:
    pass

DATABASE_ENGINE = DATABASES['default']['ENGINE']

# This must go _after_ the cache backends are configured, which could be in
# local settings
from django.template.loader import add_to_builtins
add_to_builtins('cachebuster.templatetags.cachebuster')

if not DEBUG:
    # if not `running in runserver` would be a better condition here
    TEMPLATE_LOADERS = (
            ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
            )

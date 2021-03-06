
import os
from decouple import config
 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = config('SECRET_KEY')
REFRESH_SECRET_KEY =config('REFRESH_SECRET_KEY')

DEBUG = config('DEBUG',cast=bool)

INSTALLED_APPS = [
    'adminlte3',
    'adminlte3_theme',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'rest_framework',
    'comments',
    'posts',
    'templates',
    'markdown',
    'django_editorjs_fields',
    'mptt'
]
ALLOWED_HOSTS = ['0.0.0.0','127.0.0.1','sheltered-journey-30026.herokuapp.com']


# Application definition


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blogBackend.urls'
# TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    )
}

WSGI_APPLICATION = 'blogBackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
#'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('NAME'),
        'HOST':config('HOST'),
        'PORT':5432,
        'USER':config('USER'),
        'PASSWORD':config('PASSWORD')
    }
}
# postgres://bjileynlnjxyjf:79b4884c310ecd09b50f3c0dcbb102cee7304507436cda289f132de1f93e9b48@ec2-54-211-160-34.compute-1.amazonaws.com:5432/datsl1e8l5o49q

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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



# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# STATICFILES_DIRS = [
#     BASE_DIR/"static",
#     '/var/www/static/',
# ]
STATIC_URL = '/static/'
STATIC_ROOT=os.path.join(BASE_DIR,'saticfiles')
STATICFILES_DIRS = [
    "static",
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIAFILES_DIRS = [
    "media",
]
AUTH_USER_MODEL='users.Register'


# message sending

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD =config('EMAIL_HOST_PASSWORD')
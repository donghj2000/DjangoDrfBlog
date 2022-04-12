"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 2.2.23.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3p--&e$%^%71)ijd@td7e2=s9gdlxalogjkor@_f#@47+sc=qo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'haystack',
    'rest_framework',
    'corsheaders',
    'drf_yasg',
	'django_filters',
    'common',
    'blog'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'store.disable.DisableCSRF',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ()
CORS_ALLOW_METHODS = (
    'DELETE','GET','OPTIONS','PATCH','POST','PUT','VIEW'
    '',
)

ROOT_URLCONF = 'project.urls'

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
                #'social_django.context_processors.backends',
                #'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.weibo.WeiboOAuth2',
    # 'social_core.backends.qq.QQOAuth2',
    # 'social_core.backends.weixin.WeixinOAuth2',
    # 'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

import datetime
JWT_EXPIRE_DAYS=7
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=JWT_EXPIRE_DAYS), 
    'JWT_AUTH_HEADER_PREFIX': 'JWT',   
    'JWT_AUTH_COOKIE': 'JwtCookie',                   
    'JWT_RESPONSE_PAYLOAD_HANDLER':'common.views.my_jwt_response_payload_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=JWT_EXPIRE_DAYS),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=JWT_EXPIRE_DAYS),
    'JWT_EXPIRE_DAYS': JWT_EXPIRE_DAYS,  #我自己添加的
    'AUTH_HEADER_TYPES': ('Bearer','SimpleJwt'),
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data/db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'common.User'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITE_ID = 1
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'upload')
MEDIA_URL = "/upload/"
UPLOAD_URL = 'upload'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'upload'),
)

STATIC_URL = '/static/'

# 第三方登录，里面的值是你的开放平台对应的值
SOCIAL_AUTH_WEIBO_KEY = '2343452354'
SOCIAL_AUTH_WEIBO_SECRET = '2345e324164ffea24'

SOCIAL_AUTH_GITHUB_KEY = '321354642131'
SOCIAL_AUTH_GITHUB_SECRET = '34654313465465465413413'

SOCIAL_AUTH_QQ_KEY = 'xxxxxxx'
SOCIAL_AUTH_QQ_SECRET = 'xxxxxxx'

SOCIAL_AUTH_WEIXIN_KEY = 'xxxxxxx'
SOCIAL_AUTH_WEIXIN_SECRET = 'xxxxxxx'
#登录成功后跳转到首页
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/index/'


# HAYSTACK_CONNECTIONS = {
#     'default': {       
#         'ENGINE': 'haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'vueblog',
#    },
# }

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'project.whoosh_cn_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

# 实时更新索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'xxxxxxxx@qq.com'
EMAIL_HOST_PASSWORD = 'xxxxxxxxxx'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
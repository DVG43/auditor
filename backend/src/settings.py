import os
from datetime import timedelta
from pathlib import Path

# from firebase_admin import initialize_app, credentials


DEBUG = os.environ.get("DEBUG", True)
SECRET_KEY = os.environ.get("SECRET_KEY")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")
BASE_DIR = Path(__file__).parent
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '*').split(',')
# CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '*').split(',')
CORS_ALLOW_ALL_ORIGINS = True
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

DJANGO_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_cleanup',
    'nested_inline',
    'templated_email',
    # 'fcm_django',
    'django_celery_beat',
    'drf_spectacular',
    'storages',
    'social_django',
    'channels',
    "graphene_django",
]

PROJECT_APPS = [
    'objectpermissions',
    'common',
    'projects',
    'trash',
    'storyboards',
    'contacts',
    'subscription',
    'tinkoff_pay',
    'timing',
    'document',
    'folders',
    'poll'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'
ASGI_APPLICATION = 'asgi.application'
# DJANGO_ALLOW_ASYNC_UNSAFE = True

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('CHANNEL_LAYERS_HOSTS'), 6379)], #127.0.0.1' redis://redis
        },
    },
}
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("API_PG_DB"),
        "USER": os.environ.get("API_PG_USER"),
        "PASSWORD": os.environ.get("API_PG_PASSWORD"),
        "HOST": os.environ.get("API_PG_HOST"),
        "PORT": os.environ.get("API_PG_PORT"),
    },
}

if ENVIRONMENT == "production" or ENVIRONMENT == "development":
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": os.path.join(BASE_DIR, "postgres_ssl.crt"),
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

# USE_L10N = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

USE_TZ = True

FIRST_DAY_OF_WEEK = 1

STATIC_URL = "/statics/"
STATIC_ROOT = os.path.join(BASE_DIR, "share", "auditor-v2_statics")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "share", "auditor-v2_media")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=300),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),

}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),

    'TEST_REQUEST_DEFAULT_FORMAT': 'json',

    'UPLOADED_FILES_USE_URL': os.environ.get('UPLOADED_FILES_USE_URL'),

    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),

    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'promocodes': os.environ.get('PROMOCODES_THROTTLE_RATE', '10/minute'),
        'users': '20/minute',
        'password_reset': os.environ.get('PASSWORD_RESET_THROTTLE_RATE', '2/minute'),
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

AUTH_USER_MODEL = 'accounts.User'

if ENVIRONMENT == "local":
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')

EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

AUTHENTICATION_BACKENDS = (
    # 'drf_social_oauth2.backends.DjangoOAuth2',
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.mailru.MRGOAuth2',
    'social_core.backends.yandex.YandexOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    "graphql_jwt.backends.JSONWebTokenBackend",
    'django.contrib.auth.backends.ModelBackend'
)

ACTIVATE_JWT = True

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',

    'social_core.pipeline.social_auth.associate_by_email',

    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'DOC_EXPANSION': 'none',
    'USE_SESSION_AUTH': False
}

# cred = credentials.Certificate(os.path.join(BASE_DIR, 'credentials.json'))
# FIREBASE_APP = initialize_app(cred)
#
# FCM_DJANGO_SETTINGS = {
#         "FCM_SERVER_KEY": os.environ.get('FSM_SERVER_KEY')
# }

# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     }
# }

SPECTACULAR_SETTINGS = {
    'TITLE': 'Auditor-v2 API',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'CAMELIZE_NAMES': True,
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields'
    ],
}

IMAGES_FOLDER_PATH = os.path.join(MEDIA_ROOT, 'images')

VIDEO_FOLDER_PATH = os.path.join(MEDIA_ROOT, 'video')

AUDIO_FOLDER_PATH = os.path.join(MEDIA_ROOT, 'audio')

AWS_S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
AWS_QUERYSTRING_AUTH = True

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_VK_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_VK_OAUTH2_KEY')
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_VK_OAUTH2_SECRET')
SOCIAL_AUTH_YANDEX_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_YANDEX_OAUTH2_KEY')
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_YANDEX_OAUTH2_SECRET')
SOCIAL_AUTH_MAILRU_KEY = os.environ.get('SOCIAL_AUTH_MAILRU_KEY')
SOCIAL_AUTH_MAILRU_SECRET = os.environ.get('SOCIAL_AUTH_MAILRU_SECRET')

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['last_name', 'first_name', 'email']
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_USER_MODEL = 'accounts.User'
SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    # 'response_type': 'token',
    'approval_prompt': 'auto'
}
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
# LOGIN_URL = 'login'
# LOGOUT_URL = 'logout'
# LOGOUT_REDIRECT_URL = '/'

os.environ['IS_TEST'] = 'False'
USE_S3 = True

DISK_SIZE = 5*1024*1024*1024
DISK_SIZE_GB = 5

# я добавил
DATA_UPLOAD_MAX_NUMBER_FIELDS = 70240

GRAPHENE = {
    "SCHEMA": "graphql_utils.schema.schema",
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

GRAPHQL_JWT = {
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_VERIFY_EXPIRATION": False,
    "JWT_DECODE_HANDLER": "graphql_utils.utils_graphql.jwt_decode",
}

REL_DOCS = [
    'storyboards',
    'links',
    'files',
    'texts',
    'timings',
    'documents',
    'folders'
]

api_key = os.environ.get('API_KEY')

from pathlib import Path
import os

# === Base ===
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-secret-key-change-me')
DEBUG = False  # DEV ONLY — we will turn off in production later
ALLOWED_HOSTS = ["alhadidtestingsite.pythonanywhere.com", "al-hadidfoundation.org"]  # DEV ONLY

# === Installed apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'website',
    'admin_panel.apps.AdminPanelConfig',
]

# === Middleware ===
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
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure' 
ROOT_URLCONF = 'alhadid_foundation.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "website.context_processors.site_settings",  # <= hii context processor mpya
            ],
            "builtins": [
                "django.templatetags.static",
                "django.contrib.humanize.templatetags.humanize",  # intcomma n.k. zipatikane kila template
                "admin_panel.templatetags.form_extras",               # tel_link, wa_link (kama uliweka)
            ],
        },
    },
]

WSGI_APPLICATION = 'alhadid_foundation.wsgi.application'

# === Database (DEV) ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === Password validation ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === i18n / tz ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

# === Static & Media ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === Auth redirects ===
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

# === Email (DEV - Gmail SMTP) ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fmklinkcompany@gmail.com'  # DEV ONLY
EMAIL_HOST_PASSWORD = 'jkxb wwru lodv qier'   # DEV ONLY
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Password reset token lifetime (seconds)
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24  # 24 hours

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cookies & session
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
# Shorter admin sessions are safer
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Transport security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
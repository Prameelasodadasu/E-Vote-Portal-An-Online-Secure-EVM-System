"""
Django settings for evm_portal project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-default-key-here-change-me')
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    # --- JAZZMIN MUST BE FIRST ---
    'jazzmin',
    # -----------------------------
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'accounts',
    'elections',
    'voting',
    'audit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'evm_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Tells Django to look in this folder
        'APP_DIRS': True, # Tells Django to look in app folders (for Jazzmin)
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

WSGI_APPLICATION = 'evm_portal.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# --- Your Keys (Twilio, Encryption, Blockchain) ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
VOTE_ENCRYPTION_KEY = os.environ["VOTE_ENCRYPTION_KEY"].encode()
GANACHE_URL = "http://127.0.0.1:7545"
VOTE_LEDGER_CONTRACT_ADDRESS = '0x6ef09EF1cbc5915a2b258Bd051ED518727846E71'
VOTE_LEDGER_CONTRACT_ABI = """
[
	{ "inputs": [{"internalType": "uint256", "name": "_electionId", "type": "uint256"}, {"internalType": "string", "name": "_voterHash", "type": "string"}], "name": "recordVote", "outputs": [], "stateMutability": "nonpayable", "type": "function" },
	{ "inputs": [], "stateMutability": "nonpayable", "type": "constructor" },
	{ "anonymous": false, "inputs": [{"indexed": true, "internalType": "uint256", "name": "electionId", "type": "uint256"}, {"indexed": true, "internalType": "string", "name": "voterHash", "type": "string"}], "name": "VoteRecorded", "type": "event" },
	{ "inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function" }
]
"""
# --- End Keys ---


# --- JAZZMIN SETTINGS ---
JAZZMIN_SETTINGS = {
    "site_title": "E-Vote Admin",
    "site_header": "E-Vote Portal",
    "site_brand": "E-Vote Admin",
    "welcome_sign": "Welcome to the E-Voting Admin Panel",
    "copyright": "E-Vote Portal Ltd",
    "search_model": "auth.User",
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/"},
        {"model": "auth.User"},
    ],

    "custom_links": {
        "elections": [{
            "name": "📊 Vote Tally Chart", 
            "url": "/admin/elections/election/tally/", 
            "icon": "fas fa-chart-bar",
            "permissions": ["elections.view_election"]
        }]
    },

    "ui_tweaks": {
        "navbar_small_text": False,
        "footer_small_text": False,
        "body_small_text": False,
        "brand_small_text": False,
        "brand_colour": "navbar-primary",
        "accent": "accent-primary",
        "navbar": "navbar-dark",
        "no_navbar_border": False,
        "navbar_fixed": True,
        "layout_boxed": False,
        "footer_fixed": False,
        "sidebar_fixed": True,
        "sidebar": "sidebar-dark-primary",
        "sidebar_nav_small_text": False,
        "sidebar_disable_expand": False,
        "sidebar_nav_child_indent": False,
        "sidebar_nav_compact_style": True, 
        "sidebar_nav_legacy_style": False,
        "sidebar_nav_flat_style": True, 
        "theme": "lux", 
        "dark_mode_theme": "darkly", 
        "button_classes": {
            "primary": "btn-outline-primary",
            "secondary": "btn-outline-secondary",
            "info": "btn-info",
            "warning": "btn-warning",
            "danger": "btn-danger",
            "success": "btn-success"
        }
    }
}
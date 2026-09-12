from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'dev-only-reconciliation-key'


DEBUG = True


ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'reconciliation-engine-vivf.onrender.com',
]


INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'corsheaders',
    'reconciler',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]


ROOT_URLCONF = 'core.urls'


TEMPLATES = []


WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


USE_TZ = True


CORS_ALLOWED_ORIGINS = [
    'https://reconciliation-engine-three.vercel.app',
]
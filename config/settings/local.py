"""
Local settings

- Run in Debug mode

- Use console backend for emails

- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env(
    "DJANGO_SECRET_KEY", default="S5JB.fGgmQiIv[y0B=VAV!J#C|isQ^mG|(&ZVw_j-#V<fbI;uX"
)

# Mail settings
# ------------------------------------------------------------------------------

EMAIL_PORT = 1025

EMAIL_HOST = "localhost"
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)


# CACHING
# ------------------------------------------------------------------------------
REDIS_MAX_CONNECTIONS = env.int("REDIS_MAX_CONNECTIONS", default=1)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": REDIS_MAX_CONNECTIONS,
                "timeout": 20,
            },
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,  # mimics memcache behavior. http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        },
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INSTALLED_APPS += ["debug_toolbar"]

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["django_extensions"]

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Site URL
SITE_URL = env("SITE_URL", default="http://localhost:8000")

# Github credentials
GITHUB_USERNAME = env("GITHUB_USERNAME")
GITHUB_PASSWORD = env("GITHUB_PASSWORD")
GITHUB_WEBHOOK_SECRET = env("GITHUB_WEBHOOK_SECRET")

# YouTube
YOUTUBE_API_KEY = env("YOUTUBE_API_KEY")

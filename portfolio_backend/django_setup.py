import django
from django.conf import settings
import os
import sys


def setup():
    if not settings.configured:
        # Detect if running on Render or locally
        is_render = "RENDER" in os.environ

        if is_render:
            # PostgreSQL on Render
            databases = {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": os.getenv("PGDATABASE", "portfolio"),
                    "USER": os.getenv("PGUSER", "postgres"),
                    "PASSWORD": os.getenv("PGPASSWORD", ""),
                    "HOST": os.getenv("PGHOST", "localhost"),
                    "PORT": os.getenv("PGPORT", "5432"),
                }
            }
        else:
            # SQLite locally
            db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "portfolio.db"
            )
            databases = {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": db_path,
                }
            }

        settings.configure(
            DEBUG=not is_render,
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
            DATABASES=databases,
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            USE_TZ=True,
        )
        django.setup()

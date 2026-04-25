import django
from django.conf import settings
import os
import sys


def setup():
    if not settings.configured:
        # Detect if PostgreSQL is available (Render injects PGHOST when DB is linked)
        has_postgres = "PGHOST" in os.environ

        if has_postgres:
            # PostgreSQL on Render (when linked)
            databases = {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": os.getenv("PGDATABASE", "portfolio"),
                    "USER": os.getenv("PGUSER", "postgres"),
                    "PASSWORD": os.getenv("PGPASSWORD", ""),
                    "HOST": os.getenv("PGHOST"),
                    "PORT": os.getenv("PGPORT", "5432"),
                }
            }
        else:
            # SQLite locally and on Render (without linked DB)
            db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "portfolio.db"
            )
            databases = {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": db_path,
                }
            }

        is_render = "RENDER" in os.environ
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

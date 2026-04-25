import django
from django.conf import settings
import os
import sys


def setup():
    if not settings.configured:
        # Use absolute path for database
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "portfolio.db"
        )

        settings.configure(
            DEBUG=True,
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": db_path,
                }
            },
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            USE_TZ=True,
        )
        django.setup()

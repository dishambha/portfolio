"""
Migration setup script - initializes the database tables using Django ORM.
"""

import os

os.environ.setdefault("DJANGO_DB_PATH", "portfolio.db")

import django_setup

django_setup.setup()

from django.db import connection
from models import ContactMessage

print("Setting up database...")

# Create tables using Django's schema editor
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(ContactMessage)
    print("✓ ContactMessage table created successfully!")

print("✓ Database setup complete!")

# Verify the table exists
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='models_contactmessage';"
    )
    result = cursor.fetchone()
    if result:
        print(f"✓ Confirmed: Table 'models_contactmessage' exists")

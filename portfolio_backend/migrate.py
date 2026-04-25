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
    if (
        not connection.introspection.table_names()
        or "portfolio_contactmessage" not in connection.introspection.table_names()
    ):
        schema_editor.create_model(ContactMessage)
        print("✓ Created ContactMessage table")
    else:
        print("✓ Table already exists")
    print("✓ ContactMessage table created successfully!")

print("✓ Database setup complete!")

# Verify the table exists
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_contactmessage';"
    )
    result = cursor.fetchone()
    if result:
        print(f"✓ Confirmed: Table 'portfolio_contactmessage' exists")

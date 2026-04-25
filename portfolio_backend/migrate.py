"""
Migration setup script - initializes the database tables using Django ORM.
"""

import os
import django_setup

django_setup.setup()

from django.db import connection
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from models import ContactMessage

print("Setting up database...")

# Create all required tables
with connection.schema_editor() as schema_editor:
    # Create contenttypes table first (required by Django)
    if "django_content_type" not in connection.introspection.table_names():
        schema_editor.create_model(ContentType)
        print("✓ Created ContentType table")

    # Create auth table if needed
    if "auth_user" not in connection.introspection.table_names():
        schema_editor.create_model(User)
        print("✓ Created User table")

    # Create ContactMessage table
    if "portfolio_contactmessage" not in connection.introspection.table_names():
        schema_editor.create_model(ContactMessage)
        print("✓ Created ContactMessage table")
    else:
        print("✓ ContactMessage table already exists")

print("✓ Database setup complete!")

# Verify the table exists
tables = connection.introspection.table_names()
if "portfolio_contactmessage" in tables:
    print(f"✓ Confirmed: All required tables exist ({len(tables)} tables)")
else:
    print("✗ ERROR: ContactMessage table was not created!")
    exit(1)

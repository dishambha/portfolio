"""
Migration setup script - initializes the database tables using Django ORM.
Runs on every app start to ensure tables exist.
"""

import os
import sys
import traceback

try:
    import django_setup

    django_setup.setup()

    from django.db import connection
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import User
    from models import ContactMessage

    print("[Migration] Starting database setup...")

    # Create all required tables
    with connection.schema_editor() as schema_editor:
        # Create contenttypes table first (required by Django)
        if "django_content_type" not in connection.introspection.table_names():
            schema_editor.create_model(ContentType)
            print("[Migration] ✓ Created ContentType table")

        # Create auth table if needed
        if "auth_user" not in connection.introspection.table_names():
            schema_editor.create_model(User)
            print("[Migration] ✓ Created User table")

        # Create ContactMessage table
        if "portfolio_contactmessage" not in connection.introspection.table_names():
            schema_editor.create_model(ContactMessage)
            print("[Migration] ✓ Created ContactMessage table")
        else:
            print("[Migration] ✓ ContactMessage table already exists")

    # Verify the table exists
    tables = connection.introspection.table_names()
    if "portfolio_contactmessage" in tables:
        print(f"[Migration] ✓ Database setup complete! ({len(tables)} tables)")
    else:
        print("[Migration] ✗ ERROR: ContactMessage table was not created!")
        sys.exit(1)

except Exception as e:
    print(f"[Migration] ✗ FATAL ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

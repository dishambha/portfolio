#!/usr/bin/env python
"""Django management utility."""

import os
import sys
import django_setup

if __name__ == "__main__":
    django_setup.setup()
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

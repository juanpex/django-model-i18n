#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")

if __name__ == "__main__":
    try:
        from django.core.management import execute_manager
        import settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
        execute_manager(settings)
    except ImportError:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)

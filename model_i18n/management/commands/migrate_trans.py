# -*- coding: utf-8 -*-
import sys
import os
import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Migrate apps configured in TRANSLATED_APP_MODELS."

    def handle(self, *args, **options):
        if 'south' in settings.INSTALLED_APPS:
            do_migrate = False
            do_schema = False
            do_initial = False
            app_label = "All"
            try:
                 do_migrate = (args[0] == "migrate")
                 do_schema = (args[0] == "schema")
                 do_initial = (args[0] == "initial")
                 app_label = args[1]
            except:
                do_initial = True
            from model_i18n.conf import TRANSLATED_APP_MODELS
            for app_path in TRANSLATED_APP_MODELS:
                app_name = app_path.split(".")[-1]
                if app_label != app_name and app_label != "All":
                    continue
                mig_path = 'model_i18n.migrations.' + app_name
                if do_initial:
                    try:
                        call_command('convert_to_south', app_name)
                    except:
                        pass
                if do_schema:
                    call_command('schemamigration', app_name, auto=True)
                if do_migrate:
                    call_command('migrate', app_name)
        else:
            pass
            #TODO: Generate dumpdata, reset and loaddata

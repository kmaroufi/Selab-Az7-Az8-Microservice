import asyncio
import threading

from asgiref.sync import async_to_sync
from django.apps import AppConfig
# import asyncio

from django.utils.decorators import classonlymethod


class UsersappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usersapp'

    def ready(self):
        # from usersapp.ns import setup_sync
        # setup_sync()
        from usersapp import nc
        asyncio.get_event_loop().create_task(nc.setup())
        print("ready")

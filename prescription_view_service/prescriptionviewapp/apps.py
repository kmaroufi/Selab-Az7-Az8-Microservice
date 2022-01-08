import threading
import time
import asyncio
import nats

from django.apps import AppConfig
from prescriptionviewapp import nc


class PrescriptionviewappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescriptionviewapp'

    def ready(self):
        asyncio.get_event_loop().create_task(nc.setup())
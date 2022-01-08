import asyncio

from django.apps import AppConfig


class PrescriptionappConfig(AppConfig):
    name = 'prescriptionapp'
    def ready(self):
        from prescriptionapp.nc import setup
        # asyncio.get_event_loop()
        asyncio.get_event_loop().create_task(setup())
        pass

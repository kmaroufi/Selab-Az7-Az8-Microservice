import asyncio

import schedule
from django.apps import AppConfig

from datetime import datetime


class StatisticsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'statisticsapp'

    def ready(self):
        from statisticsapp import nc
        asyncio.get_event_loop().create_task(nc.setup())
        schedule.every().day.at("00:00:05").do(create_daily_statistic)


def create_daily_statistic():
    from statisticsapp.models import DailyStatistic
    if DailyStatistic.objects.filter(date=datetime.now()).count() == 0:
        DailyStatistic(date=datetime.now()).save()

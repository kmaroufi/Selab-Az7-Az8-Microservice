# Create your views here.
import json
import uuid
from datetime import datetime

from asgiref.sync import async_to_sync, sync_to_async
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import classonlymethod
from django.views import View
import asyncio
import nats

from statisticsapp.models import DailyStatistic


class DailyStatisticView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request, year, month, day):
        try:
            statistic = await sync_to_async(DailyStatistic.objects.values().get)(date=datetime(year, month, day))
            print(statistic)
            return JsonResponse(statistic)
        except Exception as e:
            return JsonResponse({'result': 'error', 'message': str(e)})

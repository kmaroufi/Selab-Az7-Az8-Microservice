import json
from datetime import datetime

import nats
from django.http import JsonResponse
from django.shortcuts import render
from asgiref.sync import sync_to_async

# Create your views here.
import asyncio
from django.utils.decorators import classonlymethod
from django.views import View
# import aiohttp
import requests
from asgiref.sync import sync_to_async

from prescriptionviewapp import models
from prescriptionviewapp.models import Prescription, Patient, Doctor
from prescriptionviewapp.nc import handle_new_prescription


class PrescriptionsView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request):
        user_type = request.GET.get('for', None)
        # print(datetime.now())
        cursor = int(request.GET.get("cursor", 0))
        limit = int(request.GET.get("limit", 10))
        limit = min(limit, 100)
        if cursor < 0:
            cursor = 0
        if limit < 0:
            limit = 0
        if user_type is None:
            prescriptions = await sync_to_async(
                lambda: Prescription.objects().exclude('prescription_id').order_by("-date_time")[
                        cursor: cursor + limit])()
            prescriptions = [ob.to_mongo().to_dict() for ob in prescriptions]
            return JsonResponse({'prescriptions': prescriptions})
        else:
            national_code = request.GET.get('national_code', None)
            prescriptions = []
            if user_type == "patient":
                prescriptions = await sync_to_async(lambda: Prescription.objects(patient_national_code=national_code)
                                                    .exclude('prescription_id')
                                                    .order_by("-date_time")[cursor: cursor + limit])()
            elif user_type == "doctor":
                prescriptions = await sync_to_async(lambda: Prescription.objects(doctor_national_code=national_code)
                                                    .exclude('prescription_id')
                                                    .order_by("-date_time")[cursor: cursor + limit])()
            prescriptions = [ob.to_mongo().to_dict() for ob in prescriptions]
            return JsonResponse({'prescriptions': prescriptions})

    @staticmethod
    def get_person_info(national_code, is_patient):
        r = requests.get('127.0.0.1/%s:15000' % 'patient' if is_patient else 'doctor',
                         params={"national_code": national_code})
        return r.json()['form']


class PatientsView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def post(self, request):
        national_code = request.POST["national_code"]
        name = request.POST["name"]

        try:
            if national_code == "":
                raise Exception("national code can not be empty")
            if name == "":
                raise Exception("name can not be empty")
            await sync_to_async(Patient(national_code=national_code, name=name).save)()
            return JsonResponse({'result': 'success'})
        except Exception as e:
            return JsonResponse({'result': 'error', 'message': str(e)})


class DoctorsView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def post(self, request):
        national_code = request.POST["national_code"]
        name = request.POST["name"]

        try:
            if national_code == "":
                raise Exception("national code can not be empty")
            if name == "":
                raise Exception("name can not be empty")
            await sync_to_async(Doctor(national_code=national_code, name=name).save)()
            return JsonResponse({'result': 'success'})
        except Exception as e:
            return JsonResponse({'result': 'error', 'message': str(e)})

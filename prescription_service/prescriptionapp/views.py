# Create your views here.
import json
import uuid
from datetime import datetime

from asgiref.sync import async_to_sync, sync_to_async
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import classonlymethod
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
import asyncio
import nats

from prescriptionapp.models import Patient, Doctor
from prescriptionapp.nc import js, nc, setup

setup_called = False


class PrescriptionsView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def post(self, request):
        global setup_called

        print(request.POST)

        doctor_national_code = request.POST["doctor_national_code"]
        patient_national_code = request.POST["patient_national_code"]
        drug_list = request.POST["drug_list"]
        comment = request.POST["comment"]

        if drug_list == "":
            return JsonResponse({'result': 'error', 'message': "drug list can not be empty"})

        try:
            await sync_to_async(check_existence)(patient_national_code, doctor_national_code)
        except Patient.DoesNotExist as e:
            return JsonResponse({'result': 'error', 'message': str(e)})
        except Doctor.DoesNotExist as e:
            return JsonResponse({'result': 'error', 'message': str(e)})

        try:
            inbox = nc.new_inbox()
            sub = await nc.subscribe(inbox)
            ack = await js.publish("new_prescription",
                                   json.dumps({"date_time": str(datetime.now()),
                                               "prescription_id": str(uuid.uuid4()),
                                               "doctor_national_code": doctor_national_code,
                                               "patient_national_code": patient_national_code,
                                               "drug_list": drug_list,
                                               "comment": comment,
                                               "inbox": inbox}).encode())
            print(ack)
            msg = await sub.next_msg()
            asyncio.create_task(sub.unsubscribe())
            print(msg)
            return JsonResponse({'result': 'success'})
        except Exception as e:
            print(str(e))
            if js is None and not setup_called:
                setup_called = True
                asyncio.create_task(setup())
            return JsonResponse({'result': 'error', 'message': str(e)})


class PatientsView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def post(self, request):
        national_code = request.POST["national_code"]

        try:
            if national_code == "":
                raise Exception("national code can not be empty")
            await sync_to_async(Patient(national_code=national_code).save)()
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

        try:
            if national_code == "":
                raise Exception("national code can not be empty")
            await sync_to_async(Doctor(national_code=national_code).save)()
            return JsonResponse({'result': 'success'})
        except Exception as e:
            return JsonResponse({'result': 'error', 'message': str(e)})


def check_existence(patient_national_code, doctor_national_code):
    Patient.objects.get(national_code=patient_national_code)
    Doctor.objects.get(national_code=doctor_national_code)

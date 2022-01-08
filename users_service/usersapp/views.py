import asyncio
import base64
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse

from usersapp.models import Patient, NewPatientEvent, delete_new_patient_event, Doctor, NewDoctorEvent, \
    delete_new_doctor_event, Admin
from usersapp.nc import js, publish_new_patient_event, publish_new_doctor_event

# Create your views here.
from django.utils.decorators import classonlymethod
from django.views import View
from asgiref.sync import sync_to_async
import jwt

# print("a")
jwt_secret = 'microservice'


class PatientsView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def post(self, request):
        global setup_called
        print(request.POST)
        name = request.POST["name"]
        national_code = request.POST["national_code"]
        password = request.POST["password"]

        try:
            await sync_to_async(self.insert_patient_to_db)(national_code, name, password)
        except ValidationError as e:
            print(str(e))
            return JsonResponse({'result': 'fail', 'message': str(e)})
        except Exception as e:
            print(str(e))
            return JsonResponse(
                {'result': 'fail', 'message': 'a patient with national code %s existed' % national_code})

        await publish_new_patient_event(national_code, name)

        return JsonResponse({'result': 'success'})

    async def get(self, request):
        patients = None
        cursor = int(request.GET.get("cursor", 0))
        limit = int(request.GET.get("limit", 10))
        limit = min(limit, 100)
        if cursor < 0:
            cursor = 0
        if limit < 0:
            limit = 0
        try:
            patients = await sync_to_async(
                lambda: list(Patient.objects.values('national_code', 'name')[cursor: cursor + limit]))()
            return JsonResponse({'patients': patients})
        except Exception as e:
            print(e)
            return JsonResponse({'result': 'error', 'message': e})

    @transaction.atomic
    def insert_patient_to_db(self, national_code, name, password):
        with transaction.atomic():
            patient = Patient(national_code=national_code, name=name, password=password)
            patient.full_clean()
            patient.save(force_insert=True)
            NewPatientEvent(national_code=national_code, name=name, password=password).save()


class PatientFindView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request, national_code):
        patient = None
        try:
            patient = await sync_to_async(Patient.objects.values('national_code', 'name').get)(
                national_code=national_code)
            return JsonResponse({'patient': patient})
        except Exception as e:
            print(e)
            return JsonResponse({'result': 'error', 'message': str(e)})


class DoctorsView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def post(self, request):
        print(request)
        name = request.POST["name"]
        national_code = request.POST["national_code"]
        password = request.POST["password"]

        try:
            await sync_to_async(self.insert_doctor_to_db)(national_code, name, password)
        except ValidationError as e:
            print(str(e))
            return JsonResponse({'result': 'fail', 'message': str(e)})
        except Exception as e:
            print(str(e))
            return JsonResponse({'result': 'fail', 'message': 'a doctor with national code %s existed' % national_code})

        await publish_new_doctor_event(national_code, name)

        return JsonResponse({'result': 'success'})

    async def get(self, request):
        doctors = None
        cursor = int(request.GET.get("cursor", 0))
        limit = int(request.GET.get("limit", 10))
        limit = min(limit, 100)
        if cursor < 0:
            cursor = 0
        if limit < 0:
            limit = 0
        try:
            doctors = await sync_to_async(
                lambda: list(Doctor.objects.values('national_code', 'name')[cursor: cursor + limit]))()
            return JsonResponse({'doctors': doctors})
        except Exception as e:
            print(e)
            return JsonResponse({'result': 'error', 'message': e})

    @transaction.atomic
    def insert_doctor_to_db(self, national_code, name, password):
        with transaction.atomic():
            doctor = Doctor(national_code=national_code, name=name, password=password)
            doctor.full_clean()
            doctor.save(force_insert=True)
            NewDoctorEvent(national_code=national_code, name=name, password=password).save()


class DoctorFindView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request, national_code):
        doctor = None
        try:
            doctor = await sync_to_async(Doctor.objects.values('national_code', 'name').get)(
                national_code=national_code)
            return JsonResponse({'doctor': doctor})
        except Exception as e:
            print(e)
            return JsonResponse({'result': 'error', 'message': str(e)})


class AdminFindView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request, user_name):
        admin = None
        try:
            admin = await sync_to_async(Admin.objects.values('user_name').get)(
                user_name=user_name)
            return JsonResponse({'admin': admin})
        except Exception as e:
            print(e)
            return JsonResponse({'result': 'error', 'message': str(e)})


class AuthView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def post(self, request):
        user_type = None
        try:
            user_type = request.GET.get('userType')
        except:
            return JsonResponse({'result': 'error', 'message': 'invalid user type'})

        # print(request.headers)
        if user_type == 'patient':
            try:
                national_code, password = base64.b64decode(request.headers.get('User-Authorization').split()[1]) \
                    .decode().split(":")

                patient = await sync_to_async(Patient.objects.get)(national_code=national_code, password=password)
                payload_data = {"national_code": national_code,
                                "user_type": "patient"}
                token = jwt.encode(payload=payload_data, key=jwt_secret)
                return JsonResponse({'access_token': token})
            except Exception as e:
                return JsonResponse({'result': 'error', 'message': 'incorrect national code or password'})
        elif user_type == 'doctor':
            try:
                national_code, password = base64.b64decode(request.headers.get('User-Authorization').split()[1]) \
                    .decode().split(":")

                doctor = await sync_to_async(Doctor.objects.get)(national_code=national_code, password=password)
                payload_data = {"national_code": national_code,
                                "user_type": "doctor"}
                token = jwt.encode(payload=payload_data, key=jwt_secret)
                return JsonResponse({'access_token': token})
            except Exception as e:
                return JsonResponse({'result': 'error', 'message': 'incorrect national code or password'})
        elif user_type == 'admin':
            try:
                user_name, password = base64.b64decode(request.headers.get('User-Authorization').split()[1]) \
                    .decode().split(":")

                admin = await sync_to_async(Admin.objects.get)(user_name=user_name, password=password)
                payload_data = {"user_name": user_name,
                                "user_type": "admin"}
                token = jwt.encode(payload=payload_data, key=jwt_secret)
                return JsonResponse({'access_token': token})
            except Exception as e:
                return JsonResponse({'result': 'error', 'message': 'incorrect user name or password'})
        else:
            return JsonResponse({'result': 'error', 'message': 'invalid user type'})

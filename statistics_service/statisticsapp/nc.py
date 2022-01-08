import json
import threading

import aiohttp
import nats
import asyncio

# nc = asyncio.get_event_loop().run_until_complete()
from asgiref.sync import sync_to_async
from django.db import transaction

nc = None
js = None


async def get_ns():
    global nc
    if nc is None:
        await setup()
    return nc


async def get_js():
    global js
    if js is None:
        await setup()
    return js


setup_called = False


async def setup():
    global setup_called
    setup_called = True
    global nc
    global js
    if nc is None:
        nc = await nats.connect("127.0.0.1:4222", reconnect_time_wait=10, max_reconnect_attempts=-1)

        # Create JetStream context.
        js = nc.jetstream()

        await js.add_stream(name="users", subjects=["new_patient", "new_doctor"])
        await js.add_stream(name="prescriptions", subjects=["new_prescription"])

        await js.subscribe("new_patient", durable="statistics_new_patient", cb=new_patient_event_cb,
                           manual_ack=True)

        await js.subscribe("new_doctor", durable="statistics_new_doctor", cb=new_doctor_event_cb,
                           manual_ack=True)
        await js.subscribe("new_prescription", durable="statistics_new_prescription",
                           cb=new_prescription_event_cb,
                           manual_ack=True)
        #
        # asyncio.create_task(repeat(15, new_users_event_handler))
        print("nc setup completed")
        return nc, js


# from statisticsapp.models import DailyStatistic

async def new_patient_event_cb(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(handle_new_patient)(msg.metadata.timestamp, info['national_code'])
    except Exception as e:
        print("couldn't save patient to database")
        return

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


async def new_doctor_event_cb(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(handle_new_doctor)(msg.metadata.timestamp, info['national_code'])
    except Exception as e:
        print("couldn't save doctor to database")
        return

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


async def new_prescription_event_cb(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(handle_new_prescription)(msg.metadata.timestamp, info['prescription_id'])
    except Exception as e:
        print("couldn't save prescription to database")
        return

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


from statisticsapp.models import DailyStatistic, Patient, Doctor, Prescription


def increase(date, prescriptions_count, patient_count, doctor_count):
    daily_statistic = None
    try:
        daily_statistic = DailyStatistic.objects.get(date=date)
    except:
        daily_statistic = DailyStatistic(date=date)

    daily_statistic.new_prescriptions_count += prescriptions_count
    daily_statistic.new_patients_count += patient_count
    daily_statistic.new_doctors_count += doctor_count

    daily_statistic.save()


@transaction.atomic
def handle_new_patient(date, national_code):
    if Patient.objects.filter(national_code=national_code).count() == 0:
        Patient(national_code=national_code).save()
        increase(date, 0, 1, 0)
    else:
        print("duplicate patient")


@transaction.atomic
def handle_new_doctor(date, national_code):
    if Doctor.objects.filter(national_code=national_code).count() == 0:
        Doctor(national_code=national_code).save()
        increase(date, 0, 0, 1)
    else:
        print("duplicate doctor")


@transaction.atomic
def handle_new_prescription(date, prescription_id):
    if Prescription.objects.filter(prescription_id=prescription_id).count() == 0:
        Prescription(prescription_id=prescription_id).save()
        increase(date, 1, 0, 0)
    else:
        print("duplicate prescription")

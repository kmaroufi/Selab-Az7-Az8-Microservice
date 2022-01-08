import json
import threading

import aiohttp
import nats
import asyncio

# nc = asyncio.get_event_loop().run_until_complete()
from asgiref.sync import sync_to_async

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

        # await js.add_stream(name="users", subjects=["new_patient", "new_doctor"])
        await js.add_stream(name="prescriptions", subjects=["new_prescription"])

        await js.subscribe("new_patient", durable="prescriptions_new_patient", cb=new_patient_event_cb,
                           manual_ack=True)

        await js.subscribe("new_doctor", durable="prescriptions_new_doctor", cb=new_doctor_event_cb,
                           manual_ack=True)
        #
        # asyncio.create_task(repeat(15, new_users_event_handler))
        print("nc setup completed")
        return nc, js

from prescriptionapp.models import Patient, Doctor


async def new_patient_event_cb(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(Patient(national_code=info['national_code']).save)()
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
        await sync_to_async(Doctor(national_code=info['national_code']).save)()
    except Exception as e:
        print("couldn't save doctor to database")
        return

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


# async def new_users_event_handler():
#     # print('new_patient_event_handler')
#
#     try:
#         events = await (sync_to_async(lambda: list(NewPatientEvent.objects.order_by('creation_time').all())))()
#         for event in events:
#             try:
#                 async with aiohttp.ClientSession() as session:
#                     async with session.post('http://127.0.0.1:8000/patients',
#                                             data={"national_code": event.national_code}) as response:
#                         print("Status:", response.status)
#                         print("Content-type:", response.headers['content-type'])
#
#                         res = await response.json()
#                         print(res)
#                     async with session.post('http://127.0.0.1:9000/patients',
#                                             data={"national_code": event.national_code,
#                                                   "name": event.name}) as response:
#                         print("Status:", response.status)
#                         print("Content-type:", response.headers['content-type'])
#
#                         res = await response.json()
#                         print(res)
#
#                 await sync_to_async(delete_new_patient_event)(event.national_code)
#
#                 print('one event successfully published and deleted from database')
#             except Exception as e:
#                 print(str(e))
#
#                 try:
#                     ack = await js.publish("new_patient",
#                                            json.dumps({"name": event.name,
#                                                        "national_code": event.national_code,
#                                                        "password": event.password}).encode(),
#                                            1)
#                     print(ack)
#
#                     await sync_to_async(delete_new_patient_event)(event.national_code)
#
#                     print('one event successfully published and deleted from database')
#                 except Exception as e:
#                     print(str(e))
#     except Exception as e:
#         print(str(e))
#
#     return
#
#     try:
#         events = await (sync_to_async(lambda: list(NewDoctorEvent.objects.order_by('creation_time').all())))()
#         for event in events:
#             try:
#                 ack = await (await get_js()).publish("new_doctor",
#                                                      json.dumps({"name": event.name,
#                                                                  "national_code": event.national_code,
#                                                                  "password": event.password}).encode())
#                 print(ack)
#
#                 await sync_to_async(event.delete)()
#             except Exception as e:
#                 print(str(e))
#
#             print('one event successfully published and deleted from database')
#     except Exception as e:
#         print(str(e))


async def repeat(interval, func, *args, **kwargs):
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(interval))

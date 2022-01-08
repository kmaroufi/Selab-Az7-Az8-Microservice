import json
import threading

import aiohttp
import nats
import asyncio

# nc = asyncio.get_event_loop().run_until_complete()
from asgiref.sync import sync_to_async
from nats.js.headers import MSG_ID_HDR

from users_service.settings import INTERNAL_SERVICE_TOKEN
from usersapp.models import NewPatientEvent, delete_new_patient_event, delete_new_doctor_event, NewDoctorEvent

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


def f(**kwargs):
    results = kwargs['results']
    results[0], results[1] = asyncio.run(setup())


def setup_sync():
    global nc
    global js
    results = [None] * 2
    t = threading.Thread(target=lambda: asyncio.run(setup(results)))
    t.start()
    t.join()
    print(results)
    print("nc setup completed")
    nc, js = results[0], results[1]
    return nc, js


# asyncio.get_event_loop().run_until_complete(setup([None] * 2))


# setup_sync()

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

        # await js.subscribe("new_patient", durable="users_new_patient", cb=new_patient_event_cb,
        #                    manual_ack=True)

        # await js.subscribe("new_doctor", durable="users_new_doctor", cb=new_doctor_event_cb,
        #                    manual_ack=True)

        asyncio.create_task(repeat(15, new_users_event_handler))
        print("nc setup completed")
        return nc, js


async def new_patient_event_cb(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(delete_new_patient_event)(info['national_code'])
    except Exception as e:
        pass

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


async def new_doctor_event_cb(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(delete_new_doctor_event)(info['national_code'])
    except Exception as e:
        pass

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


async def new_users_event_handler():
    # print('new_patient_event_handler')
    # try:
    #     if not nc.is_connected:
    #         return
    # except:
    #     return

    try:
        events = await (sync_to_async(lambda: list(NewPatientEvent.objects.order_by('creation_time').all())))()
        for event in events:
            await publish_new_patient_event(event.national_code, event.name)
    except Exception as e:
        print(str(e))

    try:
        events = await (sync_to_async(lambda: list(NewDoctorEvent.objects.order_by('creation_time').all())))()
        for event in events:
            await publish_new_doctor_event(event.national_code, event.name)
    except Exception as e:
        print(str(e))


async def repeat(interval, func, *args, **kwargs):
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(interval))


async def publish_new_patient_event(national_code, name):
    try:
        async with aiohttp.ClientSession(headers={"Authorization": "Bearer %s" % INTERNAL_SERVICE_TOKEN}) as session:
            tasks = [asyncio.create_task(session.post('http://127.0.0.1:8000/patients',
                                                      data={"national_code": national_code})),
                     asyncio.create_task(session.post('http://127.0.0.1:9000/patients',
                                                      data={"national_code": national_code, "name": name}))]
            responses = await asyncio.gather(*tasks)
            for response in responses:
                # print("Status:", response.status)

                res = await response.json()
                assert (res['result'] == 'success')
                print(res)

            ack = await js.publish("new_patient",
                                   json.dumps({"name": name,
                                               "national_code": national_code}).encode(),
                                   timeout=0.5)
            print(ack)

            await sync_to_async(delete_new_patient_event)(national_code)

            print('one event successfully published and deleted from database')

    except Exception as e:
        print(str(e))


async def publish_new_doctor_event(national_code, name):
    try:
        async with aiohttp.ClientSession(headers={"Authorization": "Bearer %s" % INTERNAL_SERVICE_TOKEN}) as session:
            tasks = [asyncio.create_task(session.post('http://127.0.0.1:8000/doctors',
                                                      data={"national_code": national_code})),
                     asyncio.create_task(session.post('http://127.0.0.1:9000/doctors',
                                                      data={"national_code": national_code, "name": name}))]
            responses = await asyncio.gather(*tasks)
            for response in responses:
                # print("Status:", response.status)

                res = await response.json()
                assert (res['result'] == 'success')
                print(res)

        ack = await js.publish("new_doctor",
                               json.dumps({"name": name,
                                           "national_code": national_code}).encode(),
                               timeout=0.5)
        print(ack)

        await sync_to_async(delete_new_doctor_event)(national_code)

        print('one event successfully published and deleted from database')
    except Exception as e:
        print(str(e))

import json
import threading

import aiohttp
import nats
import asyncio

# nc = asyncio.get_event_loop().run_until_complete()
from asgiref.sync import sync_to_async

from prescription_view_service.settings import INTERNAL_SERVICE_TOKEN
from prescriptionviewapp.models import Patient, Prescription, Doctor

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
        # await js.add_stream(name="prescriptions", subjects=["new_prescription"])

        await js.subscribe("new_patient", durable="prescription_view_new_patient", cb=new_patient_event_handler,
                           manual_ack=True)
        await js.subscribe("new_doctor", durable="prescription_view_new_doctor", cb=new_doctor_event_handler,
                           manual_ack=True)
        await js.subscribe("new_prescription", durable="prescription_view_new_prescription",
                           cb=new_prescription_event_handler,
                           manual_ack=True)
        print("nc setup completed")
        return nc, js


async def new_patient_event_handler(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    print(msg.sid)
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(save_patient_to_database)(info['national_code'], info['name'])
    except:
        print("couldn't save patient: %s %s in database" %
              (info['national_code'], info['name']))
        return

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


async def new_doctor_event_handler(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())
    try:
        await sync_to_async(save_doctor_to_database)(info['national_code'], info['name'])
    except:
        print("couldn't save doctor: %s %s in database" %
              (info['national_code'], info['name']))
        return

    try:
        await msg.ack()
    except:
        print("couldn't send ack")


async def new_prescription_event_handler(msg):
    print("Received a message on '{subject} {reply}': {data}".format(
        subject=msg.subject, reply=msg.reply, data=msg.data))
    info = json.loads(msg.data.decode())

    try:
        if await sync_to_async(Prescription.objects(prescription_id=info['prescription_id']).count)() != 0:
            raise Exception("duplicate prescription")
    except Exception as e:
        print(str(e))
        return

    patient = None
    doctor = None
    try:
        patient = await sync_to_async(Patient.objects.get)(national_code=info['patient_national_code'])

    except Patient.DoesNotExist as e:
        async with aiohttp.ClientSession(headers={"Authorization": "Bearer %s" % INTERNAL_SERVICE_TOKEN}) as session:
            async with session.get('http://127.0.0.1:7000/patients/%s' % info['patient_national_code']) as response:
                print("Status:", response.status)
                print("Content-type:", response.headers['content-type'])

                res = await response.json()
                # assert (res['result'] == 'success')
                print(res)
                patient_info = res['patient']

                try:
                    patient = await sync_to_async(save_patient_to_database)(patient_info['national_code'],
                                                                            patient_info['name'])
                except Exception as e:
                    print("couldn't save patient: %s %s in database" %
                          (patient_info['national_code'], patient_info['name']))
                    return

    try:
        doctor = await sync_to_async(Doctor.objects.get)(national_code=info['doctor_national_code'])

    except Doctor.DoesNotExist as e:
        async with aiohttp.ClientSession(headers={"Authorization": "Bearer %s" % INTERNAL_SERVICE_TOKEN}) as session:
            async with session.get('http://127.0.0.1:7000/doctors/%s' % info['doctor_national_code']) as response:
                print("Status:", response.status)
                print("Content-type:", response.headers['content-type'])

                res = await response.json()
                # assert (res['result'] == 'success')
                print(res)
                doctor_info = res['doctor']

                try:
                    doctor = await sync_to_async(save_doctor_to_database)(doctor_info['national_code'],
                                                                          doctor_info['name'])
                except:
                    print("couldn't save doctor: %s %s in database" %
                          (doctor_info['national_code'], doctor_info['name']))
                    return

    try:
        await sync_to_async(handle_new_prescription2)(info['prescription_id'],
                                                      info['date_time'],
                                                      info['patient_national_code'],
                                                      patient.name,
                                                      info['doctor_national_code'],
                                                      doctor.name,
                                                      info['drug_list'],
                                                      info['comment'])

    except Exception as e:
        print(e)
        if e != "duplicate prescription":
            return

    try:
        await msg.ack()
        await nc.publish(info['inbox'],
                         json.dumps({"prescription_id": info['prescription_id']}).encode())
    except Exception as e:
        print(e)


def handle_new_prescription(prescription_id, date_time, patient_national_code, doctor_national_code, drug_list, comment):
    if Prescription.objects(prescription_id=prescription_id).count() != 0:
        raise Exception("duplicate prescription")

    patient = Patient.objects.get(national_code=patient_national_code)

    doctor = Doctor.objects.get(national_code=doctor_national_code)

    Prescription(prescription_id=prescription_id,
                 date_time=date_time,
                 patient_national_code=patient_national_code,
                 patient_name=patient['name'],
                 doctor_national_code=doctor_national_code,
                 doctor_name=doctor['name'],
                 drug_list=drug_list,
                 comment=comment).save()


def handle_new_prescription2(prescription_id, date_time, patient_national_code, patient_name, doctor_national_code, doctor_name,
                             drug_list, comment):
    Prescription(prescription_id=prescription_id,
                 date_time=date_time,
                 patient_national_code=patient_national_code,
                 patient_name=patient_name,
                 doctor_national_code=doctor_national_code,
                 doctor_name=doctor_name,
                 drug_list=drug_list,
                 comment=comment).save()


def save_patient_to_database(national_code, name):
    return Patient(national_code=national_code, name=name).save()


def save_doctor_to_database(national_code, name):
    return Doctor(national_code=national_code, name=name).save()


# def check_pending_prescriptions():
#     while True:
#         pending_prescription = PendingPrescription.objects().order_by('id', 'number_of_tries')[0]
#
#         if pending_prescription is not None:
#             try:
#                 patient_info = NewPrescription.get_person_info(pending_prescription.patient_national_code, True)
#             except:
#                 print("pending prescriptions: %s problem in fetching patient info" % pending_prescription.id)
#                 try:
#                     pending_prescription.number_of_tries += 1
#                     pending_prescription.save()
#                     print(
#                         "pending prescriptions: %s to be scheduled due to problem in fetching patient info after %s tries"
#                         % (pending_prescription.id, pending_prescription.number_of_tries))
#                     continue
#                 except:
#                     print(
#                         "pending prescriptions: %s couldn't increase number of tries in database" % pending_prescription.id)
#                     continue
#
#             try:
#                 doctor_info = NewPrescription.get_person_info(pending_prescription.doctor_national_code, False)
#             except:
#                 print("pending prescriptions: %s problem in fetching doctor info" % pending_prescription.id)
#                 try:
#                     pending_prescription.number_of_tries += 1
#                     pending_prescription.save()
#                     print(
#                         "pending prescriptions: %s to be scheduled due to problem in fetching doctor info after %s tries"
#                         % (pending_prescription.id, pending_prescription.number_of_tries))
#                     continue
#                 except:
#                     print(
#                         "pending prescriptions: %s couldn't increase number of tries in database" % pending_prescription.id)
#                     continue
#
#             try:
#                 Prescription(prescription_id=pending_prescription.prescription_id,
#                              patient_national_code=pending_prescription.patient_national_code,
#                              patient_name=patient_info['name'],
#                              doctor_national_code=pending_prescription.doctor_national_code,
#                              doctor_name=doctor_info['name'],
#                              drug_list=pending_prescription.drug_list,
#                              comment=pending_prescription.comment).save()
#                 print("pending prescriptions: %s successfully added to prescription database" % pending_prescription.id)
#                 try:
#                     pending_prescription.delete()
#                     print(
#                         "pending prescriptions: %s successfully deleted from pending prescription database" % pending_prescription.id)
#
#                     time.sleep(60)
#                 except:
#                     print(
#                         "pending prescriptions: %s couldn't delete from pending prescription database" % pending_prescription.id)
#                     continue
#             except:
#                 print("problem in saving prescription to database")
#                 try:
#                     pending_prescription.number_of_tries += 1
#                     pending_prescription.save()
#                     print(
#                         "pending prescriptions: %s to be scheduled due to problem in saving prescription to database after %s tries"
#                         % (pending_prescription.id, pending_prescription.number_of_tries))
#                     continue
#                 except:
#                     print(
#                         "pending prescriptions: %s couldn't increase number of tries in database" % pending_prescription.id)
#                     continue
#         else:
#             print("no pending prescription")
#             time.sleep(60)


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

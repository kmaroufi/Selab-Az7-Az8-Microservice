# from umongo.fields import *
from json import JSONEncoder

from mongoengine import *


# Create your models here.
class Prescription(Document):
    prescription_id = StringField(primary_key=True)
    date_time = DateTimeField(required=True)
    patient_national_code = StringField('^[0-9]', 10, 10, required=True)
    patient_name = StringField()
    doctor_national_code = StringField('^[0-9]', 10, 10, required=True)
    doctor_name = StringField()
    drug_list = StringField(required=True)
    comment = StringField()


class Patient(Document):
    national_code = StringField('^[0-9]', 10, 10, primary_key=True)
    name = StringField(required=True)


class Doctor(Document):
    national_code = StringField('^[0-9]', 10, 10, primary_key=True)
    name = StringField(required=True)

class MongoEncoder(JSONEncoder):
    def default(self, obj):
        return JSONEncoder.default(self, obj)

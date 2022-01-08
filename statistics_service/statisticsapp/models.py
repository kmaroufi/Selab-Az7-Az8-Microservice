from django.db import models
from django.db.models import DateField


class DailyStatistic(models.Model):
    date = DateField(primary_key=True)
    new_prescriptions_count = models.IntegerField(default=0)
    new_patients_count = models.IntegerField(default=0)
    new_doctors_count = models.IntegerField(default=0)


class Patient(models.Model):
    national_code = models.CharField(null=False, max_length=10, primary_key=True)


class Doctor(models.Model):
    national_code = models.CharField(null=False, max_length=10, primary_key=True)


class Prescription(models.Model):
    prescription_id = models.CharField(max_length=50, primary_key=True)

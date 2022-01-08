from django.db import models


class Patient(models.Model):
    national_code = models.CharField(null=False, max_length=10, primary_key=True)


class Doctor(models.Model):
    national_code = models.CharField(null=False, max_length=10, primary_key=True)

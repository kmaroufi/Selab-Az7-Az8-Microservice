from django.core.validators import RegexValidator, MinLengthValidator
from django.db import models


# Create your models here.
class Patient(models.Model):
    national_code = models.CharField(max_length=10,
                                     primary_key=True,
                                     validators=[
                                         RegexValidator('^[0-9]*$', message='national code must be only digits'),
                                         MinLengthValidator(10,
                                                            message='length of national code must '
                                                                    'be exactly 10')])
    name = models.CharField(max_length=50, validators=[MinLengthValidator(1,
                                                                          message='name must '
                                                                                  'not be empty')])
    password = models.CharField(max_length=50, validators=[MinLengthValidator(1,
                                                                              message='password must '
                                                                                      'not be empty')])


class NewPatientEvent(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True)
    national_code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)


def delete_new_patient_event(national_code):
    NewPatientEvent.objects.get(national_code=national_code).delete()


class Doctor(models.Model):
    national_code = models.CharField(max_length=10,
                                     primary_key=True,
                                     validators=[
                                         RegexValidator('^[0-9]*$', message='national code must be only digits'),
                                         MinLengthValidator(10,
                                                            message='length of national code must '
                                                                    'be exactly 10')])
    name = models.CharField(max_length=50, validators=[MinLengthValidator(1,
                                                                          message='name must '
                                                                                  'not be empty')])
    password = models.CharField(max_length=50, validators=[MinLengthValidator(1,
                                                                              message='password must '
                                                                                      'not be empty')])


class NewDoctorEvent(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True)
    national_code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)


def delete_new_doctor_event(national_code):
    NewDoctorEvent.objects.get(national_code=national_code).delete()


class Admin(models.Model):
    user_name = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=50)

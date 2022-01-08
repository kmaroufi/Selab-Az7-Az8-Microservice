from django.urls import path

from . import views

urlpatterns = [
    path('prescriptions', views.PrescriptionsView.as_view(), name='prescriptions'),
    path('patients', views.PatientsView.as_view(), name='patients'),
    path('doctors', views.DoctorsView.as_view(), name='doctors'),
]

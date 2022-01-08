from django.urls import path

from . import views

urlpatterns = [
    path('patients/<str:national_code>', views.PatientFindView.as_view(), name='patients_by_national_code'),
    path('patients', views.PatientsView.as_view(), name='patients'),
    path('doctors/<str:national_code>', views.DoctorFindView.as_view(), name='doctors_by_national_code'),
    path('doctors', views.DoctorsView.as_view(), name='doctors'),
    path('admins/<str:user_name>', views.AdminFindView.as_view(), name='admins_by_user_name'),
    path('auth', views.AuthView.as_view(), name='auth'),
]

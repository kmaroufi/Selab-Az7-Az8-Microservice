from django.urls import path

from . import views

urlpatterns = [
    path('statistics/<int:year>/<int:month>/<int:day>', views.DailyStatisticView.as_view(), name='daily_statistic'),
]
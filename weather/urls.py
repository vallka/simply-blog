from django.urls import path

from .views import *

app_name = 'weather'

urlpatterns = [
    path('', WeatherView.as_view(), name='weather'),
]

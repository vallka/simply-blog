from django.urls import path

from .views import *

app_name = 'newsletter'

urlpatterns = [
    path('pixel/', my_image, name='pixel'),
]

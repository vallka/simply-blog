from django.urls import path

from .views import *

app_name = 'castles'

urlpatterns = [
    path('', MapView.as_view(), name='map'),
]

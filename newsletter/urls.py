from django.urls import path

from .views import *

app_name = 'newsletter'

urlpatterns = [
    path('pixel/', my_image, name='pixel'),
    path('click/<str:uuid>/', click_redirect, name='click'),
    path('notification/', notification, name='notification'),
    path('sendtest/<str:slug>', sendtest, name='sendtest'),
    path('stats/<str:slug>', stats, name='stats'),
]

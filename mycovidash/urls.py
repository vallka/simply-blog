from django.urls import path

from .views import *

app_name = 'mycovidash'

urlpatterns = [
    path('', PageView.as_view(), name='mycovidash'),
    path('update', update, name='mycovidash-update'),
]

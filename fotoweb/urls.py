from django.urls import path

from .views import *

app_name = 'fotoweb'

urlpatterns = [
    path('images/', ImageListView.as_view(), name='image'),
    path('<str:album>/', ImageListView.as_view(), name='album'),
]

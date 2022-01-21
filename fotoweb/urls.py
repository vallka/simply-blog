from django.urls import path

from .views import *

app_name = 'fotoweb'

urlpatterns = [
    path('', AlbumListView.as_view(), name='albums'),
    path('i/', view_img, name='image_view'),
    path('images/', ImageListView.as_view(), name='image'),
    path('search/', ImageSearchView.as_view(), name='search'),
    path('<str:album>/', AlbumListView.as_view(), name='album'),
    path('s/<str:album>/', ImageListView.as_view(), name='album-photos'),
]

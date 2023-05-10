from django.urls import path

from .views import *

app_name = 'fotoweb'

urlpatterns = [
    path('', AlbumListView.as_view(), name='albums'),
    path('i/', view_img, name='image_view'),
    path('images/', ImageListView.as_view(), name='images'),
    path('search/', ImageSearchView.as_view(), name='search'),
    path('<str:album>/', AlbumListView.as_view(), name='album'),
    path('s/<str:album>/', ImageListView.as_view(), name='album-photos'),
    path('image/<int:pk>/<str:par>', ImageView.as_view(), name='image-w-par'),
    path('image/<int:pk>/', ImageView.as_view(), name='image'),
    path('image/<str:name>/', ImageView.as_view(), name='image'),
    path('image/<str:name>/<str:par>', ImageView.as_view(), name='image-w-par'),
    path('api/findtags/',findtags,name='findtags'),
    path('api/maketitle/',maketitle,name='maketitle'),
    path('api/getdescription/',getdescription,name='getdescription')
]

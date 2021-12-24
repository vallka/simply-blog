import re
from django.shortcuts import render
from django.views import generic
from .models import *


import logging
logger = logging.getLogger(__name__)

class ImageListView(generic.ListView):
    model = Image
    paginate_by = 200

    def get_queryset(self):
        album = self.kwargs.get('album')
        if album:
            new_album = album
            new_album = new_album.replace('¬¬','/')
            new_album = new_album.replace(' ','_')
            new_album = re.sub(r'[^/_0-9A-Za-z\-.]','_',new_album)
            new_album = new_album.replace('__','_')
            print('album:',album,new_album)

            return Image.objects.filter(no_show=0,path__icontains=new_album).order_by('name')
        else:
            return Image.objects.filter(no_show=0).order_by('-name')

class AlbumListView(generic.ListView):
    model = Album
    paginate_by = 200

    def get_queryset(self):
        return Album.objects.filter(no_show=0).order_by('position','-id')

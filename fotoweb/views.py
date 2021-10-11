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
            return Image.objects.filter(path__icontains=album).order_by('-name')
        else:
            return Image.objects.all().order_by('-name')

from django.shortcuts import render
from django.views import generic
from .models import *


import logging
logger = logging.getLogger(__name__)

class ImageListView(generic.ListView):
    model = Image
    paginate_by = 50

    def get_queryset(self):
        return Image.objects.all().order_by('-id')[:50]

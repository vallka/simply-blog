import requests
import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from fotoweb.models import *

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'mykeyworder'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        imgs = Image.objects.filter(mykeyworder_tags__isnull=True).order_by('id')
        for i in imgs:
            print(i.url)
            i.mykeyworder_tags = i.get_mykeywords()
            i.save()

        print ("DONE!")
        logger.error("DONE - %s!",self.help,)



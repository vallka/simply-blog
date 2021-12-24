from datetime import datetime, timedelta
import re
import os
import base64
from dateutil import parser

from imagekitio import ImageKit

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections

import logging
logger = logging.getLogger(__name__)

imagekit = ImageKit(
    private_key=os.environ['IMAGEKIT_PRIVATE_KEY'],
    public_key=os.environ['IMAGEKIT_PUBLIC_KEY'],
    url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT'],
)



def open_dir(dir):
    print ('dir:',dir)
    res = imagekit.list_files({'path':dir,'limit':10,'name':'*DSC*.jpg'})

    print (res)

class Command(BaseCommand):
    help = 'scan_p'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        start_dir = ''
        
        print (self.help)

        logger.info(self.help)
        open_dir(start_dir)

        print ("DONE!")
        logger.error("DONE - %s!",self.help,)





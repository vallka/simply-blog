from datetime import datetime, timedelta
import re
import os
import requests
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections
from django.utils.dateparse import parse_datetime


from gellifinsta.models import *

import logging
logger = logging.getLogger(__name__)


debugging = False


class Command(BaseCommand):
    help = 'update_insta_db'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        products = Products.objects.all()
        names= []
        for p in products:
            names.append(p.name)

        gfs = Gellifinsta.objects.filter(tags__isnull=True)

        for gf in gfs:
            text = str(gf.caption.encode('ascii',errors="ignore").decode('ascii',errors="ignore").lower()) 

            print(text)

            tags = re.findall(r'#\w+',text)
            tags = [t[1:] for t in tags]
            tags = [re.sub('^gellifique','',t) for t in tags if re.sub('^gellifique','',t)]

            for n in names:
                #if text.find(n)>=0:
                if re.search(r'\W'+n+r'\W',text,re.S):
                    tag = n.replace(' ','')
                    print('****'+tag)
                    if not tag in tags: tags.append(tag)

            tags = ['#' + t for t in tags]

            print(' '.join(tags))
            gf.tags = ' '.join(tags)
            gf.save()



        logger.error("DONE - %s! - %s, %s",self.help,)


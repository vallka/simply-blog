from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from fotoweb.models import *

import logging
logger = logging.getLogger(__name__)


import requests

def get_mykeywords(image_url):
    username = 'vallka@vallka.com'
    key = 'KYoszozpIk5Fp4QnIl5Z2PKNhsSF4n'

    response = requests.get('http://mykeyworder.com/api/v1/analyze?url=%s' % image_url,auth=(username,key))

    print(response)
    print(response.text)

    res = response.json()
    print (res)
    print (res['keywords'])
    return res['keywords']


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
            kws = get_mykeywords(i.url + '?tr=w:600')
            i.mykeyworder_tags = ', '.join(kws)
            i.save()

        print ("DONE!")
        logger.error("DONE - %s!",self.help,)



from datetime import date,datetime,timedelta

import requests
import re
import os
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections
from django.db.models import Q,Func
from django.db.models.functions import Now

from fotoweb.models import *

import logging
logger = logging.getLogger(__name__)

GRAPH_URL = 'https://graph.facebook.com/v21.0'





class Command(BaseCommand):
    help = 'insta post'

    def add_arguments(self, parser):
        pass

    last_error = {}

    def api(self, method, path, token, **params):
        """Graph API call. Returns the parsed JSON, or None on failure (self.last_error holds the error dict)."""
        params['access_token'] = token
        try:
            res = requests.request(method, f'{GRAPH_URL}/{path}', params=params, timeout=30)
            data = res.json()
        except (requests.RequestException, ValueError) as e:
            print('api error',path,e)
            logger.error('%s: %s',path,e)
            self.last_error = {}
            return None
        if res.status_code!=200 or 'error' in data:
            print('api error',path,res.text)
            logger.error(res.text)
            self.last_error = data.get('error') or {}
            return None
        return data

    def wait_for_container(self, cont_id, token, tries=15, delay=2):
        for _ in range(tries):
            data = self.api('get', cont_id, token, fields='status_code')
            if data is None:
                return False
            status = data.get('status_code')
            if status=='FINISHED':
                return True
            if status in ('ERROR','EXPIRED'):
                print('container',cont_id,status)
                logger.error('container %s %s',cont_id,status)
                return False
            time.sleep(delay)
        print('container',cont_id,'not ready after',tries*delay,'s')
        logger.error('container %s not ready',cont_id)
        return False

    def handle(self, *args, **options):
        ig_id='17841402920326860'
        token = os.environ["FB_TOKEN"]
        print (self.help,datetime.now().hour)

        #logger.info(self.help)
        n = 1  # Number of random images you want to select

        if datetime.now().hour==20:
            end_date = datetime.now() - timedelta(days=365*2)
            print (end_date)

            images = Image.objects.filter(
                Q(created_dt__lte=end_date) &
                #Q(instagram=0) &
                Q(no_show=0) &
                Q(private=0) &
                ~Q(title='') &
                ~Q(tags='') &
                ~Q(title__isnull=True) &
                ~Q(tags__isnull=True)
            ).order_by('?')[:n]

        else:    
            images = Image.objects.filter(
                #Q(created_dt__lte=end_date) &
                Q(instagram=0) &
                Q(no_show=0) &
                Q(private=0) &
                ~Q(title='') &
                ~Q(tags='') &
                ~Q(title__isnull=True) &
                ~Q(tags__isnull=True)
            ).order_by('?')[:n]

        if len(images)==0:
            print('No more images to publish')

        for i in images:
            print (i.id,i.title,i.path,i.instagram_text)

            image_url=i.url+'?tr=f-jpg'
            caption=i.instagram_text or ''

            data = self.api('post', f'{ig_id}/media', token, image_url=image_url, caption=caption)
            if data is None:
                error = self.last_error
                if error.get('error_user_title')=='Invalid aspect ratio':
                    print(error['error_user_title'],error.get('error_user_msg'))
                    ar = re.search(r"\('(\d+)\/(\d+)',\)",error.get('error_user_msg') or '')
                    if not ar:
                        return
                    w = ar.group(1)
                    h = ar.group(2)

                    print (w,h,image_url)
                    if int(w)<int(h):
                        image_url += ',ar-4-5,w-'+w
                    else:
                        image_url += ',ar-191-100,w-'+w
                    data = self.api('post', f'{ig_id}/media', token, image_url=image_url, caption=caption)
                if data is None:
                    return

            cont_id=data['id']
            print ('container',cont_id)

            # the container is processed asynchronously; publishing before it is
            # FINISHED fails with "Media ID is not available" (9007/2207027)
            if not self.wait_for_container(cont_id, token):
                return

            data = self.api('post', f'{ig_id}/media_publish', token, creation_id=cont_id)
            if data is None:
                return
            img_id=data['id']
            print ('img_id',img_id)

            data = self.api('get', img_id, token, fields='timestamp')
            if data is None:
                return
            ts=data['timestamp']
            print ('ts',ts)

            i.instagram = 1
            i.instagram_code = img_id
            i.instagram_dt = ts
            i.save()

        print ("DONE!")
        #logger.error("DONE - %s!",self.help,)

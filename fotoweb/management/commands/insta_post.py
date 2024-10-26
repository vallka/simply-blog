from datetime import date
import requests
import json
import re
from urllib.parse import quote
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections
from django.db.models import Q

from fotoweb.models import *

import logging
logger = logging.getLogger(__name__)





class Command(BaseCommand):
    help = 'insta post'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ig_id='17841402920326860'
        token = os.environ["FB_TOKEN"]


        print (self.help)

        #logger.info(self.help)
        n = 1  # Number of random images you want to select

        #start_date = date(2022, 1, 1)
        #end_date = date(2022, 12, 31)

        images = Image.objects.filter(
            #Q(date__gte=start_date) &
            #Q(date__lte=end_date) &
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
            caption=quote(i.instagram_text)

            url=f'https://graph.facebook.com/v17.0/{ig_id}/media?access_token={token}&image_url={image_url}&caption={caption}'
            res = requests.post(url)

            try:
                cont_id=json.loads(res.content)['id']
                print ('container',cont_id)
                #logger.info(f'container:{cont_id}')
            except:
                print("try0",res.text)
                logger.error(res.text)
                error = json.loads(res.text)
                print(error)
                if (error['error']['error_user_title']=='Invalid aspect ratio'):
                    print(error['error']['error_user_title'],error['error']['error_user_msg'])
                    ar = re.search(r"\('(\d+)\/(\d+)',\)",error['error']['error_user_msg'])
                    w = ar.group(1)
                    h = ar.group(2)

                    print (w,h,image_url)
                    if (w<h):
                        image_url += ',ar-4-5,w-'+w
                        url=f'https://graph.facebook.com/v17.0/{ig_id}/media?access_token={token}&image_url={image_url}&caption={caption}'
                        res = requests.post(url)

                        try:
                            cont_id=json.loads(res.content)['id']
                            print ('container',cont_id)
                            #logger.info(f'container:{cont_id}')
                        except:
                            print("try0a",res.text)
                            logger.error(res.text)
                            return
                    else:        
                        return
                else:        
                    return


            url=f'https://graph.facebook.com/v17.0/{ig_id}/media_publish?access_token={token}&creation_id={cont_id}'
            res = requests.post(url)

            try:
                img_id=json.loads(res.content)['id']
                print ('img_id',img_id)
                #logger.info(f'img_id:{img_id}')
            except:
                print("try1",res.text)
                logger.error(res.text)
                return

            url=f'https://graph.facebook.com/v17.0/{img_id}?access_token={token}&fields=timestamp'
            res = requests.get(url)
            try:
                ts=json.loads(res.content)['timestamp']
                print ('ts',ts)
                #logger.info(f'ts:{ts}')
            except:
                print("try2",res.text)
                logger.error(res.text)
                return


            i.instagram = 1
            i.instagram_code = img_id
            i.instagram_dt = ts
            i.save()

        print ("DONE!")
        #logger.error("DONE - %s!",self.help,)

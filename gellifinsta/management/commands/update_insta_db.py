from datetime import datetime, timedelta
import re
import os
import requests
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections
from django.utils.dateparse import parse_datetime

from imagekitio import ImageKit

from gellifinsta.models import *

import logging
logger = logging.getLogger(__name__)


debugging = False


imagekit = ImageKit(
    private_key='private_bGRpF4j3lmfR/vYo2ivR2VYrZMI=',
    public_key='public_pEAwf28psPyINBB0jTBnGUFKuyM=',
    url_endpoint='https://ik.imagekit.io/gellifinsta/'
)

def update_year(y):
    ff=imagekit.list_files({'limit':1000,'path':y,})

    for f in ff['response']:
        if (f['filePath'].endswith('.jpg') and
            not f['filePath'].endswith('_2.jpg') and 
            not f['filePath'].endswith('_3.jpg') and 
            not f['filePath'].endswith('_4.jpg') and 
            not f['filePath'].endswith('_5.jpg') and 
            not f['filePath'].endswith('_6.jpg') and 
            not f['filePath'].endswith('_7.jpg') and 
            not f['filePath'].endswith('_8.jpg') and 
            not f['filePath'].endswith('_9.jpg') and 
            not f['filePath'].endswith('_10.jpg') and 
            not f['filePath'].endswith('_11.jpg') and 
            not f['filePath'].endswith('_12.jpg') and 
            not f['filePath'].endswith('_13 jpg') and 
            not f['filePath'].endswith('_14.jpg') and 
            not f['filePath'].endswith('_15.jpg') and 
            not f['filePath'].endswith('_16.jpg') and 
            not f['filePath'].endswith('_17.jpg') and 
            not f['filePath'].endswith('_18.jpg') and 
            not f['filePath'].endswith('_19.jpg') and 
            not f['filePath'].endswith('_20.jpg')
        ): 
            ik_file = f['filePath']
            txt_url = f['url'].replace('.jpg','.txt')
            if txt_url.endswith('_1.txt'): txt_url.replace('_1.','.')
            json_url = f['url'].replace('.jpg','.js')
            if json_url.endswith('_1.js'): json_url.replace('_1.','.')


            print(ik_file,txt_url,json_url)

            fn = ik_file[6:]
            ts = fn[0:19]
            ts = ts[0:10]+'T'+ts[11:]
            ts = ts[0:13]+':'+ts[14:]
            ts = ts[0:16]+':'+ts[17:]
            ts += 'Z'

            dts = parse_datetime(ts)
            
            sc = fn[20:].replace('_1.jpg','').replace('.jpg','')

            print(fn,ts,dts,sc)

            try:
                gi = Gellifinsta.objects.get(shortcode=sc)
            except Gellifinsta.DoesNotExist:    
                txt = requests.get(txt_url)
                txt_text = ''
                if txt.status_code==200:
                    print(txt.text)
                    print(txt.encoding)
                    txt_text = txt.text.encode('utf-8','ignore').decode('ascii','ignore')
                    print(txt_text)
                else:
                    print(txt.status_code)

                is_video=False
                json_file = requests.get(json_url)
                if json_file.status_code==200:
                    #print(json_file.text)
                    json_data = json.loads(json_file.text)
                    print (json_data['node']['is_video'])
                    is_video=json_data['node']['is_video']
                else:
                    print(json_file.status_code)
                    #print(json_file.text)


                Gellifinsta.objects.create(shortcode=sc,
                        taken_at_datetime=dts,
                        caption=txt_text,
                        file_path=f['filePath'],
                        url=f['url'],
                        username='gellifique_professional',
                        is_video=is_video,
                        )





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



        #update_year('2018')
        #update_year('2019')
        #update_year('2020')
        update_year('2021')
        return

        with connections['presta'].cursor() as cursor:
            sql = """
                SELECT p.id_product, pl.name
                FROM  `ps17_product` p 
                LEFT JOIN `ps17_product_lang` pl ON (pl.`id_product` = p.`id_product` AND pl.`id_lang` = 1 AND pl.`id_shop` = 1) 
                WHERE `active` = 1 AND state = 1 AND id_manufacturer=2
                and name>='A'
                ORDER BY  NAME                
"""

            cursor.execute(sql)
            data = cursor.fetchall()


        for d in data:
            n = d[1]

            n1 = re.sub(r'\s*\(.*?\)\s*','',n).lower()
            #n1 = re.sub(r'\s+','',n1)
            n1 = re.sub(r'[0-9/]+gr$','',n1)
            n1 = re.sub(r'[^a-z0-9_/ ]','',n1)
            n1 = re.sub(r'\s+',' ',n1)
            n2 = n1.split('/')
            n2 = [n.strip() for n in n2]
            print(n,n2)

            for n in n2:
                if not n in names:
                    names.append(n)
                    product = Products.objects.create(name=n)
                    product.save()

        print (names)
        logger.error("DONE - %s! - %s, %s",self.help,)


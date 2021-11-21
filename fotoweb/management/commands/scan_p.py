from datetime import datetime, timedelta
import re
import os
import base64
from dateutil import parser
from io import BytesIO
from iptcinfo3 import IPTCInfo

from pcloud import PyCloud
from imagekitio import ImageKit

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections

from fotoweb.models import *

import logging
logger = logging.getLogger(__name__)

imagekit = ImageKit(
    private_key=os.environ['IMAGEKIT_PRIVATE_KEY'],
    public_key=os.environ['IMAGEKIT_PUBLIC_KEY'],
    url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT'],
)

pc = PyCloud(os.environ['P_USERNAME'], os.environ['P_PASSWORD'])

cnt = 0

def open_dir(dir):
    global cnt

    print ('dir:',dir)
    ff = pc.listfolder(path=dir)
    #print(ff)

    for f in sorted(ff['metadata']['contents'],key=lambda file: file['path']):
        if f['isfolder']:
            open_dir (f['path'])
        else:
            if f['contenttype']=='image/jpeg' and '2048' in f['path']:
                cnt += 1
                print(cnt,f['path'])
                fdt = parser.parse(f['created'])
                new_dir = dir.replace('/Gellifique/VALYA','')
                new_dir = new_dir.replace(' ','_')
                new_dir = re.sub(r'[^/_0-9A-Za-z\-.]','_',new_dir)
                new_dir = new_dir.replace('__','_')

                fn = os.path.basename(f['path'].replace(' ','_'))
                
                res = imagekit.list_files({'path':new_dir,'name':fn})
                if res['error']:
                    print ('ERROR',res)

                #print (res)

                if not res['response'] or parser.parse(res['response'][0]['createdAt'])<fdt:
                    #fd = pc.file_open(path=f['path'],flags=os.O_BINARY)
                    fd = pc.file_open(path=f['path'],flags=os.O_RDONLY)
                    data = pc.file_read(fd=fd['fd'],count=1024*1024*100)
                    print ('len=',len(data))
                    iptc = IPTCInfo(BytesIO(data),inp_charset='utf_8',out_charset='utf_8')
                    print (iptc)

                    upload = imagekit.upload(
                            file=base64.b64encode(data),
                            file_name=fn,
                            options={
                                "folder":new_dir,
                                "use_unique_file_name":False,
                            },
                    )
                    print("Upload binary", upload)
                    pc.file_close(fd=fd)

                    try:
                        img = Image.objects.get(name=upload['response']['name'])
                    except Image.DoesNotExist:
                        img = Image(name=upload['response']['name'])
                        
                    img.path=upload['response']['filePath']
                    img.url=upload['response']['url']
                    if not img.title: img.title = iptc['headline']
                    if not img.description: img.description = iptc['caption/abstract']
                    if not img.tags: img.tags = ', '.join(iptc['keywords'])

                    img.save()
                    print('ID:',img.id)


                else:
                    pass

                        


class Command(BaseCommand):
    help = 'scan_p'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        print ("DONE!")
        logger.error("DONE - %s!",self.help,)


start_dir = '/Gellifique/VALYA/C1/foto'



open_dir(start_dir)
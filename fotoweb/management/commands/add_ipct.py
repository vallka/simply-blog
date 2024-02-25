from datetime import datetime, timedelta
import re
import os
import zlib
import base64
from dateutil import parser
from dateutil.tz import gettz
from io import BytesIO
from iptcinfo3 import IPTCInfo
from exif import Image as XImage
import pyexiv2

from pcloud import PyCloud
from imagekitio import ImageKit
from imagekitio.models.ListAndSearchFileRequestOptions import ListAndSearchFileRequestOptions
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections
from django.utils.text import slugify

from fotoweb.models import *

import logging
logger = logging.getLogger(__name__)


p_dir = 'p:/Shared/Gellifique/VALYA/'

root_dir = '/C1/foto/'

start_dir = "Spain_Autumn_23/Favara"
#start_dir = ''




def process_image(name,dirname,file_path,file_time,full_size):
    print('process_image',name,dirname)
    if full_size:
        exif = pyexiv2.Image(file_path)
        exif_title = exif.read_xmp().get('Xmp.dc.title')
        exif.close()

        if not exif_title or not exif_title.get('lang="x-default"'):
            print('will save')
            img = Image.objects.get(name=name)
            print(img.title,img.description)
            print(img.tags)
            new_tags = img.tags.split(',')

            with open(file_path, 'rb+') as f:
                with pyexiv2.ImageData(f.read()) as exif:
                    changes = {'Iptc.Application2.ObjectName': img.title,
                               'Iptc.Application2.Keywords': new_tags, 
                               'Iptc.Application2.Headline': img.title,
                               'Iptc.Application2.Caption': img.description
                              }
                    exif.modify_iptc(changes)
                    changes = {'Xmp.dc.title': img.title,
                               'Xmp.dc.description': img.description
                              }
                    exif.modify_xmp(changes)
                    # Empty the original file
                    f.seek(0)
                    f.truncate()
                    # Get the bytes data of the image and save it to the file
                    f.write(exif.get_bytes())

        #    iptc['keywords'] = new_tags
#
        #    iptc['headline'] = img.title
        #    iptc['caption/abstract'] = img.description
        #        #iptc['keywords'].append('more keywords')
        #    iptc.save_as(file_path.replace('.jpg','_iptc.jpg'))
        #    ximg = XImage(file_path.replace('.jpg','_iptc.jpg'))
        #    print('exif')
        #    print(ximg.get('image_description'))
        #    ximg.image_description = img.title
        #    #with open(file_path.replace('.jpg','_exif.jpg'), 'wb') as new_image_file:
        #    #    new_image_file.write(ximg.get_file())


    return None
                

def process_file(file_path,type):
    global last_album,albums

    dirname = file_path
    file_time = os.path.getmtime(file_path)
    dirname = dirname.replace(p_dir,'').replace(root_dir,'').replace( '\\', '/' )
    if type=='f':
        basename = os.path.basename(dirname)
        if '.jpg' in basename:
            dirname = os.path.dirname(dirname)
            #dir_short_name = re.sub(r'\/[^/]*?$','',dirname) # remove JPEG-2048' and 'JPEG-Full-size'
            #dir_title = re.sub(r'^.*\/','',dir_short_name)   # 

            #print(f"Processing file: {basename} :: {root_dir+dirname} :: {file_time}")
            img = process_image(basename,root_dir+dirname,file_path,file_time,'JPEG-Full-size' in dirname)

def walk_directory(directory_path, process_function):
    # Ensure the directory path is valid
    if not os.path.isdir(directory_path):
        raise ValueError("Invalid directory path")

    process_function(directory_path,'d')

    # Get a list of all entries in the directory (files and subdirectories)
    entries = os.listdir(directory_path)

    # Sort entries alphabetically
    entries.sort()

    for entry in entries:
        entry_path = os.path.join(directory_path, entry)
        if os.path.isfile(entry_path):
            process_function(entry_path,'f')
            None
        elif os.path.isdir(entry_path):
            process_function(entry_path,'d')
            walk_directory(entry_path, process_function)





class Command(BaseCommand):
    help = 'add_ipct'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        directory_path = p_dir + root_dir + start_dir
        walk_directory(directory_path, process_file)

        print ("DONE!")
        logger.error("DONE - %s!",self.help,)






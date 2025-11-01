from datetime import datetime, timedelta
import re
import os
from dateutil import parser
from dateutil.tz import gettz
import pyexiv2

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections
from django.utils.text import slugify

from fotoweb.models import *
from fotoweb.admin import truncate_string

import logging
logger = logging.getLogger(__name__)

def appy_exif(file_path,title,description,tags):
    with open(file_path, 'rb+') as f:
        with pyexiv2.ImageData(f.read()) as img:
            changes = {'Iptc.Application2.ObjectName': title,'Iptc.Application2.Keywords': tags,}
            img.modify_iptc(changes)
            changes = {'Xmp.dc.title': title,
                        'Xmp.dc.description': description,
                        'Xmp.dc.subject': tags,
                        'Xmp.lr.hierarchicalSubject': tags, 
                    }
            img.modify_xmp(changes)
            # Empty the original file
            f.seek(0)
            f.truncate()
            # Get the bytes data of the image and save it to the file
            f.write(img.get_bytes())

def process_file(file_path,type):

    dirname = file_path
    file_time = os.path.getmtime(file_path)
    if type=='f':
        basename = os.path.basename(dirname)
        print (f'[{basename}] {dirname} ')  
        try:
            img = Image.objects.get(name=basename)
            print('Image',img.id,img.path,img.url,img.title,img.tags,)
            tags_list = [t.strip() for t in (img.tags or '').split(',') if t.strip()]
            title = img.title

            tags_list = tags_list[0:50]
            title = truncate_string(title, 100)

            appy_exif(dirname, img.title, img.description.strip() if img.description.strip()!='' else img.title, tags_list[0:30])
        except Image.DoesNotExist:
            print(f'***Image {basename} not found***')

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
    help = 'apply_exif'

    def add_arguments(self, parser):
        parser.add_argument('dir', type=str, help='Directory to scan')

    def handle(self, *args, **options):
        directory_path = options['dir']
        print (self.help + f' dir={dir}')
        #logger.info(self.help)

        #directory_path = p_dir + root_dir + start_dir
        walk_directory(directory_path, process_file)

        print ("DONE!")
        #logger.error("DONE - %s!",self.help,)






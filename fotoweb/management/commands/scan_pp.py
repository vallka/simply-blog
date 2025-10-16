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

imagekits = []

if os.environ.get('IMAGEKIT_PRIVATE_KEY'):
    imagekit = ImageKit(
        private_key=os.environ['IMAGEKIT_PRIVATE_KEY'],
        public_key=os.environ['IMAGEKIT_PUBLIC_KEY'],
        url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT'],
    )
    imagekits.append(imagekit)

if os.environ.get('IMAGEKIT_PRIVATE_KEY_1'):
    imagekit = ImageKit(
        private_key=os.environ['IMAGEKIT_PRIVATE_KEY_1'],
        public_key=os.environ['IMAGEKIT_PUBLIC_KEY_1'],
        url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT_1'],
    )
    imagekits.append(imagekit)

if os.environ.get('IMAGEKIT_PRIVATE_KEY_2'):
    imagekit = ImageKit(
        private_key=os.environ['IMAGEKIT_PRIVATE_KEY_2'],
        public_key=os.environ['IMAGEKIT_PUBLIC_KEY_2'],
        url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT_2'],
    )
    imagekits.append(imagekit)

if os.environ.get('IMAGEKIT_PRIVATE_KEY_3'):
    imagekit = ImageKit(
        private_key=os.environ['IMAGEKIT_PRIVATE_KEY_3'],
        public_key=os.environ['IMAGEKIT_PUBLIC_KEY_3'],
        url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT_3'],
    )
    imagekits.append(imagekit)

if os.environ.get('IMAGEKIT_PRIVATE_KEY_4'):
    imagekit = ImageKit(
        private_key=os.environ['IMAGEKIT_PRIVATE_KEY_4'],
        public_key=os.environ['IMAGEKIT_PUBLIC_KEY_4'],
        url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT_4'],
    )
    imagekits.append(imagekit)


#pc = PyCloud(os.environ['P_USERNAME'], os.environ['P_PASSWORD'])

p_dir = 'd:/FOTO/vallka/'
domain = 1
#p_dir = 'd:/FOTO/Lucas/'
#domain = 2

root_dir = '/2024/'

#start_dir = '24-01 Cullera and Cullera Castle'
#start_dir = '24-06 Valencia'

#imgk_start_dir = '/C1/foto'
#imgk_nostore_dir = '/Gellifique/VALYA'
#cnt = 0

last_album = ''
albums = []

def get_imagekit_by_slug(slug):
    return imagekits[4]

    crc = zlib.crc32(bytes(slug,'utf8'))
    if crc%2:
        return imagekits[2]
    else:
        return imagekits[1]



def process_image(name,dirname,slug,file_path,file_time,full_size):
    print('process_image',name,dirname)
    #ik_dirname = dirname.replace(' ','_')
    ik_dirname = re.sub(r'[^/_0-9A-Za-z\-.]','_',dirname)
    ik = get_imagekit_by_slug(slug)
    try:
        img = Image.objects.get(name=name)
        print('Image',img.id,img.path,img.url,img.path_fs,img.url_fs,)
    except Image.DoesNotExist:
        img = Image(name=name,domain=domain)
        img.private = True
        print('Image new')

    need_upload = True
    options = ListAndSearchFileRequestOptions(
        path=ik_dirname,
        search_query=f"name='{name}'"
    )
    res = ik.list_files(options=options)
    if res.list and res.list[0]:
        print('Found on IK',res.list[0],res.list[0].updated_at,parser.parse(res.list[0].updated_at),datetime.fromtimestamp(file_time,tz=gettz('UTC')))
        if parser.parse(res.list[0].updated_at)>=datetime.fromtimestamp(file_time,tz=gettz('UTC')):
            need_upload = False

    if need_upload:
        if full_size:
            print('Needs upload FS')
            options = UploadFileRequestOptions(
                use_unique_file_name=False,
                folder=ik_dirname,
            )

            with open(file_path, 'rb') as file:
                binary_data = file.read()
                upload = ik.upload(
                        file=base64.b64encode(binary_data),
                        file_name=name,
                        options=options
                )

                print(upload.url)
                img.path_fs=dirname+'/'+name
                img.url_fs=upload.url
                img.save()

        else:
            print('Needs upload web')
            iptc = IPTCInfo(file_path,inp_charset='utf_8',out_charset='utf_8')
            ximg = XImage(file_path)
            dt = ximg.get('datetime_original')
            dt=parser.parse(dt.replace(':','-',2)+'Z',tzinfos={'GMT':gettz('UTC')})

            provider = 'google'
            options = UploadFileRequestOptions(
                use_unique_file_name=False,
                folder=ik_dirname,
                #extensions=[
                #    {
                #        "name": f"{provider}-auto-tagging",
                #        "maxTags": 25,
                #        "minConfidence": 70
                #    },
                #]
            )

            with open(file_path, 'rb') as file:
                binary_data = file.read()
                upload = ik.upload(
                        file=base64.b64encode(binary_data),
                        file_name=name,
                        options=options
                )

                print(upload.url)
                img.path=dirname+'/'+name
                img.url=upload.url
                img.created_dt = dt
                if not img.title: img.title = iptc['headline']
                if not img.description: img.description = iptc['caption/abstract']
                if not img.tags: img.tags = ','.join(iptc['keywords'])
                if upload and upload.ai_tags:
                    tags = []
                    for tag in upload.ai_tags:
                        if tag.source==f"{provider}-auto-tagging":
                            tags.append(tag.name)
                        img.google_tags = ','.join(tags)   
                        img.add_auto_tags(','.join(tags))
                img.save()
                if img.created_dt != dt:
                    img.created_dt = dt
                    img.save()

    return img
                
def process_album(title,dirname,slug):
    try:
        album = Album.objects.get(path=dirname)
        need_cover = True if not album.cover else False
        print('Album',album.title,need_cover)
    except Album.DoesNotExist:
        album = Album(path=dirname,title=title,slug=slug,domain=domain)
        album.save()
        need_cover = True
        print('Album new',album.title,need_cover)

    return need_cover



def process_file(file_path,type):
    global last_album,albums

    dirname = file_path
    file_time = os.path.getmtime(file_path)
    dirname = dirname.replace(p_dir,'').replace(root_dir,'').replace( '\\', '/' )
    if type=='f':
        basename = os.path.basename(dirname)
        if '.jpg' in basename:
            dirname = os.path.dirname(dirname)
            dir_short_name = re.sub(r'\/[^/]*?$','',dirname) # remove JPEG-2048' and 'JPEG-Full-size'
            dir_title = re.sub(r'^.*\/','',dir_short_name)   # 
            slug = slugify(dir_short_name)

            #print(f"Processing file: {basename} :: {root_dir+dirname} :: {file_time}")
            img = process_image(basename,root_dir+dirname,slug,file_path,file_time,'JPEG-Full-size' in dirname)
            if slug!=last_album:
                last_album = slug
                print(f'new album:{slug}',albums)
                if albums:
                    for a_slug in albums:
                        album = Album.objects.get(slug=a_slug)
                        album.cover = img.url
                        album.taken_dt = img.created_dt
                        album.save()
                albums = []
    elif type=='d':
        if dirname and not 'JPEG-2048' in dirname and not 'JPEG-Full-size' in dirname:
            dir_title = re.sub(r'^.*\/','',dirname)
            slug = slugify(dirname)
            print(f"Processing dir {type}: {dirname} :: {dirname} :: {dir_title} :: {slug}")
            need_cover = process_album(dir_title,root_dir+dirname,slug)
            if need_cover and slug and not slug in albums: 
                albums.append(slug)
                #print(albums)

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
    help = 'scan_pp'

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






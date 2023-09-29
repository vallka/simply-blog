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



#pc = PyCloud(os.environ['P_USERNAME'], os.environ['P_PASSWORD'])

p_dir = 'p:/Shared/Gellifique/VALYA/'

root_dir = '/C1/foto/'

start_dir = 'Spain_Autumn_23'
#start_dir = ''

imgk_start_dir = '/C1/foto'
imgk_nostore_dir = '/Gellifique/VALYA'
cnt = 0

last_album = ''
albums = []

def get_imagekit_by_slug(slug):
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
        img = Image(name=name)
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
                extensions=[
                    {
                        "name": f"{provider}-auto-tagging",
                        "maxTags": 25,
                        "minConfidence": 70
                    },
                ]
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
        album = Album(path=dirname,title=title,slug=slug)
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
                        album.save()
                albums = []
    elif type=='d':
        if not 'JPEG-2048' in dirname and not 'JPEG-Full-size' in dirname:
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


def open_dir(dir,albums_needs_cover):
    global cnt

    print ('dir:',dir)
    ff = pc.listfolder(path=dir)
    #print(ff)

    for f in sorted(ff['metadata']['contents'],key=lambda file: file['path']):
        if f['isfolder']:
            need_cover = None
            if not 'JPEG-2048' in f['path'] and not 'JPEG-Full-size' in f['path']:
                path = f['path'].replace(imgk_nostore_dir,'')
                path = path.replace(' ','_')
                path = re.sub(r'[^/_0-9A-Za-z\-.]','_',path)
                path = path.replace('__','_')
                title = path.replace(imgk_start_dir+'/','')
                title = re.sub('/[^/]*2048[^/]*','',title)
                print('>>>',path,title)
                try:
                    album = Album.objects.get(path=path)
                    need_cover = album if not album.cover else None
                except Album.DoesNotExist:
                    album = Album(path=path,title=title)
                    album.save()
                    need_cover = album

            if need_cover:
                albums_needs_cover.append(need_cover)

                print ('folders need cover:',albums_needs_cover)


            open_dir (f['path'],albums_needs_cover)
        else:
            if f['contenttype']=='image/jpeg' and 'JPEG-2048' in f['path']:
                cnt += 1
                #print(f)
                fdt = parser.parse(f['created'])
                fdtm = parser.parse(f['modified'])
                new_dir = dir.replace(imgk_nostore_dir,'')
                new_dir = new_dir.replace(' ','_')
                new_dir = re.sub(r'[^/_0-9A-Za-z\-.]','_',new_dir)
                new_dir = new_dir.replace('__','_')

                fn = os.path.basename(f['path'].replace(' ','_'))

                options = ListAndSearchFileRequestOptions(
                    path=new_dir,
                    search_query=f"name='{fn}'"
                )

                #res = imagekit.list_files({'path':new_dir,'name':fn})
                res = imagekit.list_files(options=options)
                #if res['error']:
                #    print ('ERROR',res)

                if res.list and res.list[0]:
                    #print('dates:',f['path'],parser.parse(res.list[0].updated_at),fdt,fdtm)
                    print('dirs:',f['path'],new_dir,zlib.crc32(bytes(new_dir,'utf8')) % len(imagekits))
                    #print(res['response'][0])

                if not res.list or parser.parse(res.list[0].updated_at)<fdt or parser.parse(res.list[0].updated_at)<fdtm:
                #if not res['response'] or parser.parse(res['response'][0]['updatedAt'])<fdt or parser.parse(res['response'][0]['updatedAt'])<fdtm:
                #if not res['response']:
                    #fd = pc.file_open(path=f['path'],flags=os.O_BINARY)
                    fd = pc.file_open(path=f['path'],flags=os.O_RDONLY)
                    data = pc.file_read(fd=fd['fd'],count=1024*1024*100)
                    print ('len=',len(data))
                    iptc = IPTCInfo(BytesIO(data),inp_charset='utf_8',out_charset='utf_8')
                    print (iptc)

                    provider = 'aws';

                    options = UploadFileRequestOptions(
                        use_unique_file_name=False,
                        folder=new_dir,
                    )

                    upload = imagekit.upload(
                            file=base64.b64encode(data),
                            file_name=fn,
                            options=options
                    )
                    print("Upload binary", upload)
                    pc.file_close(fd=fd)

                    try:
                        img = Image.objects.get(name=upload.name)
                    except Image.DoesNotExist:
                        img = Image(name=upload.name)

                    img.path=upload.file_path
                    img.url=upload.url
                    if not img.title: img.title = iptc['headline']
                    if not img.description: img.description = iptc['caption/abstract']
                    if not img.tags: img.tags = ', '.join(iptc['keywords'])

                    #if not img.aws_tags and upload['response']['AITags']:
                    #    tags = []
                    #    for tag in upload['response']['AITags']:
                    #        if tag['source']==f"{provider}-auto-tagging":
                    #            print (tag)
                    #            tags.append(tag['name'])

                    #    if tags:
                    #        img.aws_tags = ','.join(tags)

                    img.save()
                    print('ID:',img.id)

                    if albums_needs_cover:
                        print ('files - cover:',albums_needs_cover)
                        for album_needs_cover in albums_needs_cover:
                            album_needs_cover.cover = img.url
                            album_needs_cover.save()
                        albums_needs_cover.clear()

                else:
                    pass
                    if albums_needs_cover:
                        print ('files - cover:',albums_needs_cover)
                        for album_needs_cover in albums_needs_cover:
                            #album_needs_cover.cover = res['response'][0]['url']
                            album_needs_cover.cover = res.list[0].url
                            album_needs_cover.save()
                        albums_needs_cover.clear()




class Command(BaseCommand):
    help = 'scan_pp'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        directory_path = p_dir + root_dir + start_dir
        walk_directory(directory_path, process_file)

        print ("DONE!")
        logger.error("DONE - %s!",self.help,)






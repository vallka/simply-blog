from ftplib import FTP_TLS,FTP
import os
import re
import requests
import csv
from django.core.management.base import BaseCommand, CommandError

#import logging
#logger = logging.getLogger(__name__)

n=0
nblocks=1

def callback(p):
    global n
    n +=1
    print(int (100 * n / nblocks),'%',end='\r')


def upload_shutter():
    global n,nblocks
    host='ftps.shutterstock.com'
    user=os.environ.get('SHUTTER_USER')
    passwd=os.environ.get('SHUTTER_PASSWORD')
    #file ="p:/Shared/Gellifique/VALYA/C1/fotoarchive/Scotland Summer 23/Lucas on Loch Lomond/JPEG-Full-size/23-06-22-DSC02854-1.jpg"
    blocksize=8192*100
    rootdir = "p:/Shared/Gellifique/VALYA"
    url='https://www.vallka.com/media/shutterstock.csv'

    r=requests.get(url)
    files=[]
    reader = csv.reader(r.text.splitlines(), delimiter=',')
    for row in reader:
        print(row)
        if '.jpg' in row[5]: files.append(row[5])


    for f in files:
        ffile = re.sub(r'JPEG-2048[^/]*\/','JPEG-Full-size/',f)
        file = rootdir + ffile
        file = file.replace ('/','\\' )
        file_stats = os.stat(file)
        nblocks = file_stats.st_size / blocksize
        print(file,nblocks)

    n=0
    with FTP_TLS(host) as ftp:
        ftp.connect(host, 21)
        ftp.auth()
        ftp.prot_p()
        ftp.login(user, passwd)
        #ftp.set_debuglevel(2)
        #ftp.login()
        ftp.dir()
        for f in files:
            n=0
            ffile = re.sub(r'JPEG-2048[^/]*\/','JPEG-Full-size/',f)
            file = rootdir + ffile
            file = file.replace ('/','\\' )
            file_stats = os.stat(file)
            nblocks = file_stats.st_size / blocksize
            print(file)
            ftp.storbinary('STOR '+os.path.basename(file), open(file, 'rb'),callback=callback,blocksize=blocksize)        


class Command(BaseCommand):
    help = 'upload shutterstock'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        #logger.info(self.help)

        upload_shutter()

        print ("DONE!")
        #logger.error("DONE - %s!",self.help,)






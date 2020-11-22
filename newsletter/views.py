import uuid
import os

from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

from .models import *

# Create your views here.

def my_image(request):
    uuid=request.GET['uuid']

    logger.error("my_image - uuid:%s",uuid)
    try:
        ns = NewsShot.objects.get(uuid=uuid)
        if ns.opened_dt==None:
            ns.opened_dt = timezone.now()
            ns.save()
    except NewsShot.DoesNotExist:
        logger.error("NewsShot.DoesNotExist:%s",uuid)


    return redirect('/static/images/pixel.png')

def click_redirect(request,uuid):
    path=request.GET['path']
    print ('click_redirect',uuid,path)
    logger.error("click_redirect - uuid:%s, path:%s",uuid,path)
    try:
        ns = NewsShot.objects.get(uuid=uuid)
        if ns.clicked_dt==None:
            ns.clicked_dt = timezone.now()
            ns.clicked_qnt = 1
        else:    
            ns.clicked_qnt += 1
        ns.save()

    except NewsShot.DoesNotExist:
        logger.error("NewsShot.DoesNotExist:%s",uuid)

    return redirect('/' + path)


@csrf_exempt
@require_POST
def notification(request):

    print('notification')
    logger.error("notification")

    filename = str(uuid.uuid1())+ '.json'

    f = open(os.path.join(settings.MEDIA_ROOT,filename)   ,'wb')
    f.write(request.body)
    f.close()

    return HttpResponse(os.path.join(settings.MEDIA_URL,filename))
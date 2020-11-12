from django.shortcuts import redirect
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)

from .models import *

# Create your views here.

def my_image(request):
    uuid=request.GET['uuid']

    logger.error("my_image - uuid:%s",uuid)
    try:
        ns = NewsShot.objects.get(uuid=uuid)
        if ns.opened_dt!=None:
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
        if ns.clicked_dt!=None:
            ns.clicked_dt = timezone.now()
            ns.clicked_qnt = 1
        else:    
            ns.clicked_qnt += 1
        ns.save()
        
    except NewsShot.DoesNotExist:
        logger.error("NewsShot.DoesNotExist:%s",uuid)

    return redirect('/' + path)

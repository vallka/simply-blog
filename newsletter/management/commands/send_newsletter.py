from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from blog.models import *
from newsletter.models import *

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'send newsletter'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger.info(self.help)
        print(self.help)

        #today = datetime.today().date() # get a Date object
        today = timezone.now() # get a Date object
        logger.info(today)

        newsletter_post = Post.objects.filter(email=True,email_send_dt__lt=today).order_by('-id')

        print(newsletter_post)

        if len(newsletter_post) > 0:
            print(newsletter_post[0])


        logger.error("DONE - %s! - %s",self.help,str(today))
        print("DONE - %s! - %s" % (self.help,str(today)))

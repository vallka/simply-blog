from datetime import datetime, timedelta
import re
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections

from gellifinsta.models import *

import logging
logger = logging.getLogger(__name__)


debugging = False

class Command(BaseCommand):
    help = 'scan_p'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        print ("DONE - %s!" % self.help)
        logger.error("DONE - %s!",self.help,)


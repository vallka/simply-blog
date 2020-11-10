from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'crontest'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        today = datetime.today().date() # get a Date object
        logger.info(today)

        logger.error("DONE - %s! - %s",self.help,str(today))

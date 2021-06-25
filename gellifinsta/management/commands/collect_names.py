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
    help = 'collect_names'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (self.help)
        logger.info(self.help)

        products = Products.objects.all()

        names= []
        for p in products:
            names.append(p.name)

        with connections['presta'].cursor() as cursor:
            sql = """
                SELECT p.id_product, pl.name
                FROM  `ps17_product` p 
                LEFT JOIN `ps17_product_lang` pl ON (pl.`id_product` = p.`id_product` AND pl.`id_lang` = 1 AND pl.`id_shop` = 1) 
                WHERE `active` = 1 AND state = 1 AND id_manufacturer=2
                and name>='A'
                ORDER BY  NAME                
"""

            cursor.execute(sql)
            data = cursor.fetchall()


        for d in data:
            n = d[1]

            n1 = re.sub(r'\s*\(.*?\)\s*','',n).lower()
            #n1 = re.sub(r'\s+','',n1)
            n1 = re.sub(r'[0-9/]+gr$','',n1)
            n1 = re.sub(r'[^a-z0-9_/ ]','',n1)
            n1 = re.sub(r'\s+',' ',n1)
            n2 = n1.split('/')
            n2 = [n.strip() for n in n2]
            print(n,n2)

            for n in n2:
                if not n in names:
                    names.append(n)
                    product = Products.objects.create(name=n)
                    product.save()

        print (names)
        logger.error("DONE - %s! - %s, %s",self.help,)


from datetime import datetime, timedelta
import urllib
import re
import time

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail,EmailMessage,EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.db import connections

from blog.models import *
from newsletter.models import *

import logging
logger = logging.getLogger(__name__)

MOCK = False


def my_replace(match):
    match1 = match.group(1)
    match2 = match.group(2)
    match3 = match.group(3)
    match3 = urllib.parse.quote_plus(match3)

    return f'{match1}{match2}blog/newsletter/click/####uuid####/?path={match3}'

class Command(BaseCommand):
    help = 'send newsletter'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger.info(self.help)
        print(self.help)

        sent = 0
        not_sent = 0
        dolog = False

        #today = datetime.today().date() # get a Date object
        today = timezone.now() # get a Date object
        #logger.info(today)

        newsletter_post = Post.objects.filter(email=True,email_send_dt__lt=today,email_status__in=[Post.EmailStatus.NONE,Post.EmailStatus.SENDING]).order_by('id')


        if len(newsletter_post) > 0:
            html = NewsShot.add_html(newsletter_post[0].formatted_markdown,newsletter_post[0].title,newsletter_post[0].slug,newsletter_post[0].title_color,newsletter_post[0].title_bgcolor)
            #print(self.add_html(newsletter_post[0].formatted_markdown,newsletter_post[0].title,newsletter_post[0].slug))

            custs = self.get_customers(newsletter_post[0].id)
            #custs = self.get_customers_eu(newsletter_post[0].id)

            if len(custs):
                dolog = True

                if newsletter_post[0].email_status==Post.EmailStatus.NONE:
                    newsletter_post[0].email_status = Post.EmailStatus.SENDING
                    newsletter_post[0].save()

                for i,c in enumerate(custs):
                    print(f"{i+1}, customer:{c[0]}:{c[1]}")
                    #logger.info(f"{i+1}, customer:{c[0]}:{c[1]}")

                    shot = NewsShot(blog=newsletter_post[0],customer_id=c[0])

                    if self.send(c,html,newsletter_post[0].title,shot.uuid):

                        shot.send_dt = timezone.now()
                        shot.save() 

                        sent += 1
                    else:
                        not_sent += 1

            else:
                dolog = True
                print('no more customers! - setting SENT status')
                logger.info('no more customers! - setting SENT status')
                newsletter_post[0].email_status = Post.EmailStatus.SENT
                newsletter_post[0].save()
        else:
            #logger.info('no newsletters to send!')
            print('no newsletters to send!')

        print("DONE! - %s! Sent:%s, Not sent:%s" % (self.help,str(sent),str(not_sent)))
        if dolog:
            logger.error("DONE! - %s! Sent:%s, Not sent:%s",self.help,str(sent),str(not_sent))



    def encode_urls(self,html,uuid):
        html = re.sub(r'(<a\s+href=")(https://www\.gellifique\.co.uk/)([^"]*)',my_replace,html)
        html = html.replace('####uuid####',uuid)
        return html


    def send(self,cust,html,title,uuid):
        #to_email = 'vallka@vallka.com'
        to_email = cust[1]
        html = self.encode_urls(html,str(uuid))

        #print (html)
        if not MOCK:
            email = EmailMultiAlternatives( title, title, settings.EMAIL_FROM_USER, [to_email], headers = {'X-gel-id': str(uuid)}   )
            email.attach_alternative(html, "text/html") 
            #if attachment_file: email.attach_file(attachment_file)
            
            send_result = email.send()
            print('send_result',send_result)
            time.sleep(0.5)
            return send_result

        return 1



    def get_customers(self,blog_id):

        if not MOCK:
            with connections['default'].cursor() as cursor:
                sql = """
                SELECT id_customer,email,firstname,lastname,id_lang FROM gellifique_new.ps17_customer c 
                    where active=1 and newsletter=1 and id_shop=1
                    and c.id_customer not IN (
                    select customer_id from dj.newsletter_newsshot where customer_id=c.id_customer
                    and blog_id=%s
                    )
                    ORDER BY c.id_customer  DESC
                    limit 0,50
                """
                ###    and c.email like '%%@vallka.com'

                cursor.execute(sql,[blog_id,])
                row = cursor.fetchall()
        else:
            row = [(12345,'vallka@vallka.com','Val','Kool,1')]

        return row

    def get_customers_eu(self,blog_id):

            if not MOCK:
                with connections['default'].cursor() as cursor:
                    sql = """
                    SELECT id_customer,email,firstname,lastname,id_lang FROM gellifique_eu.ps17_customer c 
                        where active=1 and id_shop=2
                        and c.id_customer not IN (
                        select customer_id from dj.newsletter_newsshot where customer_id=c.id_customer
                        and blog_id=%s
                        )
                        ORDER BY c.id_customer  DESC
                        limit 0,50
                    """
                    ###    and c.email like '%%@vallka.com'

                    cursor.execute(sql,[blog_id,])
                    row = cursor.fetchall()
            else:
                row = [(12345,'vallka@vallka.com','Val','Kool,1')]

            return row


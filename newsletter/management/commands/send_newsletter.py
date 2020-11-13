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

        #today = datetime.today().date() # get a Date object
        today = timezone.now() # get a Date object
        logger.info(today)

        newsletter_post = Post.objects.filter(email=True,email_send_dt__lt=today,email_status__in=[Post.EmailStatus.NONE,Post.EmailStatus.SENDING]).order_by('id')


        if len(newsletter_post) > 0:
            html = self.add_html(newsletter_post[0].formatted_markdown,newsletter_post[0].title,newsletter_post[0].slug)
            #print(self.add_html(newsletter_post[0].formatted_markdown,newsletter_post[0].title,newsletter_post[0].slug))

            custs = self.get_customers(newsletter_post[0].id)

            if len(custs):

                for i,c in enumerate(custs):
                    print(f"{i+1}, customer:{c[0]}:{c[1]}")
                    logger.info(f"{i+1}, customer:{c[0]}:{c[1]}")

                    shot = NewsShot(blog=newsletter_post[0],customer_id=c[0])

                    self.send(c,html,newsletter_post[0].title,shot.uuid)

                    shot.send_dt = timezone.now()
                    shot.save() 


            else:
                print('no more customers!')
                logger.info('no more customers!')
                newsletter_post[0].email_status = Post.EmailStatus.SENT
                newsletter_post[0].save()
        else:
                logger.info('no newsletters to send!')





        logger.error("DONE - %s! - %s",self.help,str(today))
        print("DONE - %s! - %s" % (self.help,str(today)))


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
            email = EmailMultiAlternatives( title, title, settings.EMAIL_FROM_USER, [to_email]  )
            email.attach_alternative(html, "text/html") 
            #if attachment_file: email.attach_file(attachment_file)
            
            send_result = email.send()
            print('send_result',send_result)
            time.sleep(1)




    def get_customers(self,blog_id):

        if not MOCK:
            with connections['default'].cursor() as cursor:
                sql = """
                SELECT id_customer,email,firstname,lastname,id_lang FROM gellifique.ps17_customer c 
                    where active=1 and newsletter=1
                    and c.id_customer not IN (
                    select customer_id from dj.newsletter_newsshot where customer_id=c.id_customer
                    and blog_id=%s
                    )
                    and c.email like '%%@vallka.com'
                    ORDER BY c.id_customer  DESC
                    limit 0,5
                """

                cursor.execute(sql,[blog_id,])
                row = cursor.fetchall()
        else:
            row = [(12345,'vallka@vallka.com','Val','Kool,1')]

        return row


    def add_html(self,text,title,slug):
        style = """
body {
    font-family: 'Open Sans', sans-serif;
    font-size: 1rem;
    color: #7a7a7a;
    line-height: 1.25em;
    letter-spacing: initial;
    background-color: #f6f6f6;
}

.blog_content {
    margin: 0;
    padding: 0;
}

.blog_post {
    max-width: 610px;
    text-align: center;
    background-color: white;
    padding: 1rem;
    margin: auto;
        margin-top: auto;
        margin-bottom: auto;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

@media (min-width: 768px){
  .blog_post {
    border-radius: 5px;
  }
}

.blog_post .blog_header {
    background-color: #fdc5dc;
    border-radius: 5px;
    padding-top: 0.5rem;
}

.blog_post {
    text-align: center;
}

.blog_content img {
    max-width: 100%;
}

.blog_content .header {
    max-width: 642px;
    margin: 0 auto;
}

h1, h2, h3 {
    margin-top: 0;
    margin-bottom: .5rem;
    font-family: inherit;
    font-weight: 700;
    line-height: 1.1;
    color: #d73672;
    text-transform: initial;
    letter-spacing: initial;
}

.h1, h1 {
    font-size: 1.375rem;
    margin-bottom: 1.563rem;
    padding-bottom: 0.5rem;
    color: black;
}

hr {
    box-sizing: content-box;
    height: 0;
    overflow: visible;
    margin-top: 1rem;
    margin-bottom: 1rem;
    border: 0;
    border-top-color: currentcolor;
    border-top-style: none;
    border-top-width: 0px;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

a {
    color: #1a1a1a;
    text-decoration: none;
    background-color: transparent;
}

.blog_post h4, .blog_post h5, .blog_post h6 {
    text-transform: initial;
    letter-spacing: initial;
    font-size: 1rem;
    color: white;
}

.blog_post h4 a, .blog_post h5 a, .blog_post h6 a {
    color: white;
}

.blog_post h4:hover, .blog_post h5:hover, .blog_post h6:hover {
  background-color: #f766a2;
  color: #fff;
  text-decoration: none;
}

.blog_post h4 a:hover, .blog_post h5 a:hover, .blog_post h6 a:hover {
  color: #fff;
  text-decoration: none;
}

.blog_post h4, .blog_post h5, .blog_post h6 {
    text-transform: initial;
    letter-spacing: initial;
    font-size: 1rem;
    background-color: #d73672;
    color: white;
    display: inline-block;
    padding: 1rem;
    border-radius: 5px;
}

footer {
    text-align: center;
    font-size: 0.8rem;
    font-style: italic;
}
.social {
    text-align: center;
}
.social i {
    color: #d73672;
}

        """

        html = f"""
<html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">

        <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;700&family=Roboto:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"> 
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">

        <title>{title}</title>
        <style>
            {style}
        </style>
    </head>
   <body>
        <img src="https://www.gellifique.co.uk/blog/newsletter/pixel/?uuid=####uuid####" style="display:none">
        <div class="blog_content">
            <div class="header"><img src="https://www.gellifique.co.uk/static/images/newsletter_header.jpg"></div>
            <div class="blog_post">

                <div class="blog_header">
                    <h1><a href="https://www.gellifique.co.uk/blog/{slug}">{title}</a></h1>
                </div>
                <div class="blog_body">


    <!-- start text -->
    {text}
    <!-- end text -->

    <p><img src="https://www.gellifique.co.uk/static/images/newsletter_footer.png"</p>

                </div>
                <div class="social">
                    <a href="https://www.facebook.com/gellifiqueltd/" target="_blank"><i class="fa fa-2x fa-facebook-square" aria-hidden="true"></i></a>
                    <a href="https://www.instagram.com/gellifique_gel_colour/" target="_blank"><i class="fa fa-2x fa-instagram" aria-hidden="true"></i></a>
                    <a href="https://www.youtube.com/channel/UC8EB7U4DV4n_8BY8wprBXOQ" target="_blank"><i class="fa fa-2x fa-youtube-square" aria-hidden="true"></i></a>
                    <a href="https://twitter.com/gellifique" target="_blank"><i class="fa fa-2x fa-twitter-square" aria-hidden="true"></i></a>
                    <a href="https://uk.pinterest.com/gellifique/" target="_blank"><i class="fa fa-2x fa-pinterest-square" aria-hidden="true"></i></a>
                </div>
            </div>
        </div>

        <footer>
            <a href="https://www.gellifique.co.uk/en/identity">unsubscribe from this list</a> |     
            <a href="https://www.gellifique.co.uk/en/identity">update subscription preferences</a>
        </footer>
    </body>
</html>
        """

        return html




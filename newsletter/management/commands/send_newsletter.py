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


        if len(newsletter_post) > 0:
            print(self.add_html(newsletter_post[0].formatted_markdown,newsletter_post[0].title))


        logger.error("DONE - %s! - %s",self.help,str(today))
        print("DONE - %s! - %s" % (self.help,str(today)))



    def add_html(self,text,title):
        style = """
body {
    font-family: 'Open Sans', sans-serif;
    font-size: 1rem;
    color: #7a7a7a;
    line-height: 1.25em;
    letter-spacing: initial;
}

.blog_content {
    background-color: #f6f6f6;
    margin-top: 1rem;
    padding-bottom: 2rem;
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

        """

        html = f"""
<html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            {style}
        </style>
    </head>
    <body>
        <div class="blog_content">
            <div class="blog_post">
                <div class="blog_header">
                    <h1><a href="/blog/early-black-friday-event-tonight/">Early Black Friday Event Tonight</a></h1>
                </div>
                <div class="blog_body">


    <p><img src=""https://www.gellifique.co.uk/static/images/newsletter_header.jpg"</p>

    {text}
    <p><img src=""https://www.gellifique.co.uk/static/images/newsletter_footer.png"</p>

                </div>
            </div>
        </div>

        <footer>
            <a href="#">unsubscribe from this list</a> |     <a href="#">update subscription preferences</a>
        </footer>
    </body>
</html>
        """

        return html




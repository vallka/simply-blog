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
            print(self.add_html(newsletter_post[0].formatted_markdown,newsletter_post[0].title,newsletter_post[0].slug))


        logger.error("DONE - %s! - %s",self.help,str(today))
        print("DONE - %s! - %s" % (self.help,str(today)))



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
        <img src="https://www.gellifique.co.uk/newsletter/pixel/" style="display:none">
        <div class="blog_content">
            <div class="header"><img src="https://www.gellifique.co.uk/static/images/newsletter_header.jpg"></div>
            <div class="blog_post">

                <div class="blog_header">
                    <h1><a href="https://www.gellifique.co.uk/blog/{slug}">{title}</a></h1>
                </div>
                <div class="blog_body">


    <p><img src="https://www.gellifique.co.uk/static/images/newsletter_header.jpg"</p>

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




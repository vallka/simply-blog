import uuid

from django.db import models

from blog.models import *

# Create your models here.
class NewsShot(models.Model):
    class Meta:
        ordering = ['-id']

    uuid = models.UUIDField(db_index=True, default=uuid.uuid1, editable=True,unique=True)
    blog = models.ForeignKey(Post,on_delete=models.CASCADE,)
    customer_id = models.IntegerField(db_index=True)
    send_dt = models.DateTimeField(blank=True, null=True)
    received_dt = models.DateTimeField(blank=True, null=True)
    opened_dt = models.DateTimeField(blank=True, null=True)
    clicked_dt = models.DateTimeField(blank=True, null=True)
    clicked_qnt = models.IntegerField(blank=True, null=True)
    note = models.CharField(blank=True, null=True, max_length=25)

    @staticmethod
    def add_html(text,title,slug,title_color,title_bgcolor):

        style = """

.blog_content {
  font-family: arial, sans-serif !important;
  font-size: 1rem !important;
  color: #232323 !important;
  background-color: #f6f6f6 !important;
  line-height: 1.1em !important;
  letter-spacing: initial !important;
  margin: 0 !important;
  padding: 0 !important;
}

@media (max-width: 768px){
  .blog_content {
    font-size: 1.25rem !important;
    line-height: 1.25em !important;
  }
}

h1, h2, h3, h4, h5, h6 {
  font-weight: 700 !important;
}



.blog_post {
    max-width: 610px !important;
    text-align: center !important;
    background-color: white !important;
    padding: 1rem !important;
    margin: auto !important;
        margin-top: auto !important;
        margin-bottom: auto !important;
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
}

@media (min-width: 768px){
  .blog_post {
    border-radius: 5px !important;
  }
}

.blog_post .blog_header {
    background-color: #eee !important;
    border-radius: 5px !important;
    padding-top: 0.5rem !important;
}

.blog_post {
    text-align: center !important;
}

.blog_content img {
    max-width: 100% !important;
}

.blog_content .header {
    max-width: 642px !important;
    margin: 0 auto !important;
    background-color: #1a1a1a !important;
}

h1, h2, h3 {
    margin-top: 0 !important;
    margin-bottom: .5rem !important;
    font-weight: 700 !important;
    line-height: 1.1 !important;
    color: #d73672 !important;
    text-transform: initial !important;
    letter-spacing: initial !important;
}

.h1, h1 {
    font-size: 1.5rem !important;
    margin-bottom: 1.563rem !important;
    padding-bottom: 0.5rem !important;
    color: black !important;
}

.h2, h2 {
  color: #d73672 !important;
  font-size: 1.25rem !important;
}
.h3, h3 {
  color: #1a1a1a !important;
  font-size: 1.1rem !important;
}

.navbar {
  background-color: #1a1a1a !important;
}

a.navbar-item {
  color: #fff !important;
  margin: 2px 2px;
  font-size: 10px !important;
  background-color: #1a1a1a !important;
  text-transform: uppercase !important;
}

a.navbar-item:hover {
    color: #d73672 !important;
}

.breadcrumb {
  padding: .75rem 1rem !important;
  margin-bottom: 1rem !important;
  list-style: none !important;
  background-color: #f6f6f6 !important;
  border-radius: 0 !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
}

hr {
    box-sizing: content-box !important;
    height: 0 !important;
    overflow: visible !important;
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
    border: 0 !important;
    border-top-color: currentcolor !important;
    border-top-style: none !important;
    border-top-width: 0px !important;
    border-top: 1px solid rgba(0, 0, 0, 0.1) !important;
}

a {
    color: #1a1a1a !important;
    text-decoration: none !important;
    background-color: transparent !important;
}

.blog_post img {
  max-width: 100%;
  display: block;
  margin: auto;
}

.blog_post p {
  text-align: left;
  margin-left: 0;
  margin-right: 0;
}

.blog_post p a {
  color: #5a5a5a;
  text-decoration: none;
  border-bottom: 3px solid #2fb5d2;
  font-weight: 600;
}


.blog_post h4, .blog_post h5, .blog_post h6 {
    text-transform: initial !important;
    letter-spacing: initial !important;
    font-size: 1rem !important;
    color: white !important;
}

.blog_post h4 a, .blog_post h5 a, .blog_post h6 a {
    color: white !important;
}

.blog_post h4:hover, .blog_post h5:hover, .blog_post h6:hover {
  background-color: #f766a2 !important;
  color: #fff !important;
  text-decoration: none !important;
}

.blog_post h4 a:hover, .blog_post h5 a:hover, .blog_post h6 a:hover {
  color: #fff !important;
  text-decoration: none !important;
}

.blog_post h4, .blog_post h5, .blog_post h6 {
    text-transform: initial !important;
    letter-spacing: initial !important;
    font-size: 1rem !important;
    background-color: #444 !important;
    color: white !important;
    display: inline-block !important;
    padding: 1rem !important;
    border-radius: 5px !important;
}

.blog_post ol, .blog_post ul {
    margin-top: 0;
    text-align: left;
    margin-left: 1rem;
    margin-right: 1rem;
}

footer {
    text-align: center !important;
    font-size: 0.8rem !important;
}
.social {
    text-align: center !important;
}

footer .www a {
    /*color: #d73672 !important;*/
    color: #1a1a1a !important;
    
}
footer .www {
    font-size: 1rem;
    padding-bottom: 1rem;
}

footer .unsubscribe {
    font-style: italic !important;
}
.social i {
    /*color: #d73672 !important;*/
    color: #1a1a1a !important;
}

.social img {
    width: 2rem;
}
        """
        style2 = ''

        if title_color:
            style2 += f"""

.blog_post .blog_header, .blog_post .blog_header a {{
    color: {title_color} !important;
}}

            """

        if title_bgcolor:
            style2 += f"""

.blog_post .blog_header {{
    background-color: {title_bgcolor} !important;
    
}}

.blog_post p a {{
    border-bottom-color: {title_bgcolor} !important;
}}


            """


        html = f"""
<html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">

        <link rel="stylesheet" href="https://use.typekit.net/oki2ljd.css">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">

        <title>{title}</title>
        <style>
            {style}
            {style2}
        </style>
    </head>
   <body>
        <img src="https://www.gellifique.co.uk/blog/newsletter/pixel/?uuid=####uuid####" style="display:none">
        <div class="blog_content">
            <div class="header"><img class="logo img-responsive" src="https://www.gellifique.co.uk/img/logo-professional-263.png" alt="GellifiQue Professional">
                <nav class="navbar">
                    <div class="navbar-menu">
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/shop-now(62)">SHOP NOW</a>
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/outlet(21)">OUTLET</a>
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/content/delivery(1)">Delivery</a>
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/content/opportunities(13)">Opportunities</a>
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/content/category/brochures(3)">BROCHURES</a>
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/content/category/health-safety(4)">HEALTH & SAFETY</a>
                        <a class="navbar-item" href="https://blog.gellifique.co.uk/blog/">BLOG</a>
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/content/SHOWROOM(12)">Showroom</a>
                        <a class="navbar-item" href="https://www.gellifique.co.uk/en/content/nail-salon(21)">Nail Salon</a>
                    </div>
                </nav>
            </div>
            <div class="blog_post">

                <div class="blog_header">
                    <h1><a href="https://blog.gellifique.co.uk/blog/{slug}">{title}</a></h1>
                </div>
                <div class="blog_body">


    <!-- start text -->
    {text}
    <!-- end text -->


    <p><img width="80%" src="https://blog.gellifique.co.uk/static/images/newsletter_footer2.png"</p>
    <hr />

                </div>
            </div>
        </div>

        <footer>
            <div class="www">
                <a href="https://www.gellifique.co.uk/">https://www.gellifique.co.uk/</a>
            </div>
            <div class="social">
                <a href="https://www.facebook.com/gellifiqueltd/" target="_blank"><img src="https://blog.gellifique.co.uk/static/images/facebook-square-brands-bl.png"></a>
                <a href="https://www.instagram.com/gellifique_gel_colour/" target="_blank"><img src="https://blog.gellifique.co.uk/static/images/instagram-square-brands-bl.png"></a>
                <a href="https://www.youtube.com/channel/UC8EB7U4DV4n_8BY8wprBXOQ" target="_blank"><img src="https://blog.gellifique.co.uk/static/images/youtube-square-brands-bl.png"></a>
                <a href="https://twitter.com/gellifique" target="_blank"><img src="https://blog.gellifique.co.uk/static/images/twitter-square-brands-bl.png"></a>
                <a href="https://uk.pinterest.com/gellifique/" target="_blank"><img src="https://blog.gellifique.co.uk/static/images/pinterest-square-brands-bl.png"></a>
            </div>
            <div class="unsubscribe">
                <a href="https://www.gellifique.co.uk/en/identity">unsubscribe from this list</a> |     
                <a href="https://www.gellifique.co.uk/en/identity">update subscription preferences</a>
            </div>
        </footer>
    </body>
</html>
        """

        #now re-do for spanish (unused now)

        html_eu = f"""
<html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">

        <link rel="stylesheet" href="https://use.typekit.net/oki2ljd.css">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">

        <title>{title}</title>
        <style>
            {style}
            {style2}
        </style>
    </head>
   <body>
        <img src="https://www.gellifique.co.uk/blog/newsletter/pixel/?uuid=####uuid####" style="display:none">
        <div class="blog_content">
            <div class="header"><img class="logo img-responsive" src="https://www.gellifique.eu/img/logo-professional-263.png" alt="GellifiQue Professional">
            </div>
            <div class="blog_post">

                <div class="blog_header">
                    <h1><a href="https://www.gellifique.co.uk/blog/{slug}">{title}</a></h1>
                </div>
                <div class="blog_body">


    <!-- start text -->
    {text}
    <!-- end text -->


    <p><img width="80%" src="https://www.gellifique.co.uk/static/images/newsletter_footer2.png"</p>
    <hr />

                </div>
            </div>
        </div>

        <footer>
            <div class="www">
                <a href="https://www.gellifique.eu/">https://www.gellifique.eu/</a>
            </div>
            <div class="social">
                <a href="https://www.facebook.com/gellifiqueltd/" target="_blank"><img src="https://www.gellifique.co.uk/static/images/facebook-square-brands.png"></a>
                <a href="https://www.instagram.com/gellifique_gel_colour/" target="_blank"><img src="https://www.gellifique.co.uk/static/images/instagram-square-brands.png"></a>
                <a href="https://www.youtube.com/channel/UC8EB7U4DV4n_8BY8wprBXOQ" target="_blank"><img src="https://www.gellifique.co.uk/static/images/youtube-square-brands.png"></a>
                <a href="https://twitter.com/gellifique" target="_blank"><img src="https://www.gellifique.co.uk/static/images/twitter-square-brands.png"></a>
                <a href="https://uk.pinterest.com/gellifique/" target="_blank"><img src="https://www.gellifique.co.uk/static/images/pinterest-square-brands.png"></a>
            </div>
            <div class="unsubscribe">
                <a href="https://gellifique.eu/es/identidad">unsubscribe from this list</a> |     
                <a href="https://gellifique.eu/es/identidad">update subscription preferences</a>
            </div>
        </footer>
    </body>
</html>
        """


        return html




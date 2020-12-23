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
    def add_html(text,title,slug):


        fa_style = r"""
@font-face {
  font-family: 'FontAwesome';
  src: url('https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/fonts/fontawesome-webfont.eot?v=4.7.0');
  src: url('https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/fonts/fontawesome-webfont.eot?#iefix&v=4.7.0') format('embedded-opentype'), 
       url('https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/fonts/fontawesome-webfont.woff2?v=4.7.0') format('woff2'), 
       url('https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/fonts/fontawesome-webfont.woff?v=4.7.0') format('woff'), 
       url('https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/fonts/fontawesome-webfont.ttf?v=4.7.0') format('truetype'), 
       url('https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/fonts/fontawesome-webfont.svg?v=4.7.0#fontawesomeregular') format('svg');
  font-weight: normal;
  font-style: normal;
}
.fa {
  display: inline-block;
  font: normal normal normal 14px/1 FontAwesome;
  font-size: inherit;
  text-rendering: auto;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
/* makes the font 33% larger relative to the icon container */
.fa-lg {
  font-size: 1.33333333em;
  line-height: 0.75em;
  vertical-align: -15%;
}
.fa-2x {
  font-size: 2em;
}
.fa-3x {
  font-size: 3em;
}
.fa-4x {
  font-size: 4em;
}
.fa-5x {
  font-size: 5em;
}
.fa-fw {
  width: 1.28571429em;
  text-align: center;
}
.fa-ul {
  padding-left: 0;
  margin-left: 2.14285714em;
  list-style-type: none;
}
.fa-ul > li {
  position: relative;
}
.fa-li {
  position: absolute;
  left: -2.14285714em;
  width: 2.14285714em;
  top: 0.14285714em;
  text-align: center;
}
.fa-li.fa-lg {
  left: -1.85714286em;
}
.fa-facebook-square:before {
  content: "\f082";
}
.fa-instagram:before {
  content: "\f16d";
}
.fa-youtube-square:before {
  content: "\f166";
}
.fa-twitter-square:before {
  content: "\f081";
}
.fa-pinterest-square:before {
  content: "\f0d3";
}
        """

        style = """
body {
    font-family: 'Open Sans', sans-serif !important;
    font-size: 1rem !important;
    color: #7a7a7a !important;
    line-height: 1.25em !important;
    letter-spacing: initial !important;
    background-color: #f6f6f6 !important;
}

.blog_content {
    margin: 0 !important;
    padding: 0 !important;
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
    background-color: #fdc5dc !important;
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
}

h1, h2, h3 {
    margin-top: 0 !important;
    margin-bottom: .5rem !important;
    font-family: inherit !important;
    font-weight: 700 !important;
    line-height: 1.1 !important;
    color: #d73672 !important;
    text-transform: initial !important;
    letter-spacing: initial !important;
}

.h1, h1 {
    font-size: 1.375rem !important;
    margin-bottom: 1.563rem !important;
    padding-bottom: 0.5rem !important;
    color: black !important;
}

.h2, h2 {
  color: #d73672 !important;
}
.h3, h3 {
  color: #1a1a1a !important;
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
    background-color: #d73672 !important;
    color: white !important;
    display: inline-block !important;
    padding: 1rem !important;
    border-radius: 5px !important;
}

footer {
    text-align: center !important;
    font-size: 0.8rem !important;
    font-style: italic !important;
}
.social {
    text-align: center !important;
}
.social i {
    color: #d73672 !important;
}

        """

        html = f"""
<html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">

        <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;700&family=Roboto:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"> 

        <title>{title}</title>
        <style>
            {fa_style}
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
            </div>
        </div>

        <footer>
            <div class="social">
                <a href="https://www.facebook.com/gellifiqueltd/" target="_blank"><i class="fa fa-2x fa-facebook-square" aria-hidden="true"></i></a>
                <a href="https://www.instagram.com/gellifique_gel_colour/" target="_blank"><i class="fa fa-2x fa-instagram" aria-hidden="true"></i></a>
                <a href="https://www.youtube.com/channel/UC8EB7U4DV4n_8BY8wprBXOQ" target="_blank"><i class="fa fa-2x fa-youtube-square" aria-hidden="true"></i></a>
                <a href="https://twitter.com/gellifique" target="_blank"><i class="fa fa-2x fa-twitter-square" aria-hidden="true"></i></a>
                <a href="https://uk.pinterest.com/gellifique/" target="_blank"><i class="fa fa-2x fa-pinterest-square" aria-hidden="true"></i></a>
            </div>

            <a href="https://www.gellifique.co.uk/en/identity">unsubscribe from this list</a> |     
            <a href="https://www.gellifique.co.uk/en/identity">update subscription preferences</a>
        </footer>
    </body>
</html>
        """

        return html




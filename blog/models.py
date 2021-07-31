import re
import requests

from bs4 import BeautifulSoup

from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


# Create your models here.
class Category(models.Model):
    class Meta:
        ordering = ['slug']

    category = models.CharField(_("Category"), blank=True, max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, max_length=100, blank=True, null=False)
    is_default = models.BooleanField(_("Default Category"),default=False)

    def __str__(self):
        return str(self.slug) + ' -- ' + str(self.category)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category)
            
        super().save(*args, **kwargs)

class Post(models.Model):
    class Meta:
        ordering = ['-id']

    title = models.CharField(_("Title"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, max_length=100, blank=True, null=False)

    blog = models.BooleanField(_("Publish to blog"),default=False)
    blog_start_dt = models.DateTimeField(_("Publish Date/Time"), blank=True, null=True)
    email = models.BooleanField(_("Send as newsletter to UK customers"),default=False)
    email_send_dt = models.DateTimeField(_("Send Date/Time"), blank=True, null=True)

    class EmailStatus(models.IntegerChoices):
        NONE = 0
        SENDING = 1
        SENT = 2

    email_status = models.IntegerField(default=EmailStatus.NONE,choices=EmailStatus.choices)

    category = models.ManyToManyField(Category, )

    title_color = models.CharField(_("Title Color"),max_length=20, blank=True, null=False, default='#232323')
    title_bgcolor = models.CharField(_("Title Bg Color"),max_length=20, blank=True, null=False, default='#eeeeee')

    text = MarkdownxField(_("Text"), blank=True, null=False)

    created_dt = models.DateTimeField(_("Created Date/Time"), auto_now_add=True, null=True)
    updated_dt = models.DateTimeField(_("Updated Date/Time"), auto_now=True, null=True)

    description  = models.TextField(_("Meta Description"), blank=True, null=False, default='')
    keywords  = models.TextField(_("Meta Keywords"), blank=True, null=False, default='')
    json_ld  = models.TextField(_("script ld+json"), blank=True, null=False, default='')


    @property
    def formatted_markdown(self):
        return markdownify(self.text)

    def __str__(self):
        return str(self.id) + ':'+ str(self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        self.look_up_gellifique_product()
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return '/blog/' + str(self.slug)        

    def look_up_gellifique_product(self):
        # [](https://www.gellifique.co.uk/en/pro-limited-edition/-periwinkle-hema-free(1342).html)

        #print ('look_up_gellifique_product')

        product_re = r"(\[\])\((https:\/\/gellifique.eu\/.+?\.html)\)"
        product_re = r"(\[\])\((https:\/\/www.gellifique.co.uk\/.+?\.html)\)"
        ##product_re = r"\((https:\/\/www.gellifique.co.uk\/.+\.html)\)"

        prods = re.findall(product_re,self.text)
        
        if prods:
            print (prods)

            for prod in prods:
                print (prod[1])
                prod_html = requests.get(prod[1])
                if prod_html.status_code == 200:
                    print ('soup::')
                    prod_html = prod_html.text

                    soup = BeautifulSoup(prod_html, 'html.parser')
                    prod_name = soup.find('h1',attrs={'itemprop':'name'})
                    prod_price = soup.find(attrs={'itemprop':'price'})
                    prod_img = soup.find('img',attrs={'itemprop':'image'})

                    print (prod_img['src'])

                    self.text = re.sub(product_re,f"![]({prod_img['src']})\n[<h4>{prod_name.text} - {prod_price.text}</h4>]({prod[1]})",self.text,1)



import requests
import os
import random

from django.db import models
from django.utils.html import mark_safe
from django.utils.text import slugify

from imagekitio import ImageKit

# Create your models here.
class Image(models.Model):
    name = models.CharField('name',max_length=100, unique=True)
    path = models.CharField('path',max_length=200, unique=True)
    url = models.CharField('url',max_length=200, unique=True)
    no_show = models.BooleanField('no show',default=False)
    created_dt = models.DateTimeField('created_dt',auto_now_add=True, null=True)
    updated_dt = models.DateTimeField('updated_dt',auto_now=True, null=True)
    mykeyworder_tags = models.TextField('mykeyworder tags',null=True, blank=True)
    adobe_tags = models.TextField('adobe tags',null=True, blank=True,)
    google_tags = models.TextField('goggle tags',null=True, blank=True,)
    aws_tags = models.TextField('aws tags',null=True, blank=True,)
    shutter_tags = models.TextField('shutter tags',null=True, blank=True,)
    title = models.CharField('title',max_length=100,null=True, blank=True)
    description = models.TextField('description',null=True, blank=True,)
    tags = models.TextField('tags',null=True, blank=True,)
    editorial = models.BooleanField('editorial',default=False)
    instagram = models.BooleanField('instagram',default=False)
    instagram_dt = models.DateTimeField('instagram_dt',null=True, blank=True,)
    instagram_code = models.CharField('instagram_code',null=True, blank=True,max_length=20)
    adobe = models.BooleanField('adobe',default=False)
    adobe_dt = models.DateTimeField('adobe_dt',null=True, blank=True,)
    shutter = models.BooleanField('shutter',default=False)
    shutter_dt = models.DateTimeField('shutter_dt',null=True, blank=True,)

    class ShutterCategories(models.TextChoices):
        EMPTY = '', ''
        Abstract = 'Abstract', 'Abstract'
        Animals = 'Animals/Wildlife', 'Animals/Wildlife'
        Backgrounds = 'Backgrounds/Textures', 'Backgrounds/Textures'	
        Beauty = 'Beauty/Fashion', 'Beauty/Fashion'	
        Buildings = 'Buildings/Landmarks', 'Buildings/Landmarks'	
        Business = 'Business/Finance', 'Business/Finance'	
        Celebrities = 'Celebrities', 'Celebrities'	
        Education = 'Education', 'Education'	
        Food = 'Food and Drink', 'Food and Drink'	
        Healthcare = 'Healthcare/Medical', 'Healthcare/Medical'	
        Holidays = 'Holidays', 'Holidays'	
        Industrial = 'Industrial', 'Industrial'	
        Interiors = 'Interiors', 'Interiors'	
        Miscellaneous = 'Miscellaneous', 'Miscellaneous'
        Objects = 'Objects', 'Objects'
        Parks = 'Parks/Outdoor', 'Parks/Outdoor'
        People = 'People', 'People'
        Religion = 'Religion', 'Religion'
        Science = 'Science', 'Science'
        Signs = 'Signs/Symbols', 'Signs/Symbols'
        Sports = 'Sports/Recreation', 'Sports/Recreation'
        Technology = 'Technology', 'Technology'
        Arts = 'The Arts', 'The Arts'
        Vintage = 'Vintage', 'Vintage'

    shutter_cat1 = models.CharField(
        max_length=50,
        choices=ShutterCategories.choices,
        default=ShutterCategories.Buildings,
    )
    shutter_cat2 = models.CharField(
        max_length=50,
        choices=ShutterCategories.choices,
        default=ShutterCategories.Parks,
    )

    pexels = models.BooleanField('pexels',default=False)
    pexels_dt = models.DateTimeField('pexels_dt',null=True, blank=True,)
    pexels_url = models.CharField('pexels_url',null=True, blank=True,max_length=200)
    rasfocus = models.BooleanField('rasfocus',default=False)
    rasfocus_dt = models.DateTimeField('rasfocus_dt',null=True, blank=True,)
    rasfocus_url = models.CharField('rasfocus_url',null=True, blank=True,max_length=200)


    def __str__(self):
        return str(self.id) + ':' + str(self.name)

    def img_tag(self):
        return mark_safe('<img src="%s" width="600" />' % (self.url + '?tr=w-600'))

    img_tag.short_description = 'Image'

    def thumb_tag(self):
        return mark_safe('<img src="%s" width="250" alt="image" />' % (self.url + '?tr=w-250'))

    thumb_tag.short_description = 'thumb'

    def tags_spaced(self):
        tags = ''
        if self.tags and len(self.tags)>len(tags): tags = self.tags
        if self.mykeyworder_tags and len(self.mykeyworder_tags)>len(tags): tags = self.mykeyworder_tags
        if self.adobe_tags and len(self.adobe_tags)>len(tags): tags = self.adobe_tags
        if self.shutter_tags and len(self.shutter_tags)>len(tags): tags = self.shutter_tags
        if self.google_tags and len(self.google_tags)>len(tags): tags = self.google_tags
        if self.aws_tags and len(self.aws_tags)>len(tags): tags = self.aws_tags
        return mark_safe('<div><span class="copy_tags">'+tags.replace(',',', ') + '</span> <a href="#" class="copy_tags">(^C)</a></div>')
    tags_spaced.short_description = 'Tags'


    def instagram_text(self):
        #tags = self.tags or self.mykeyworder_tags or self.adobe_tags or self.shutter_tags or self.google_tags or ''
        tags = ''
        if self.tags and len(self.tags)>len(tags): tags = self.tags
        if self.mykeyworder_tags and len(self.mykeyworder_tags)>len(tags): tags = self.mykeyworder_tags
        if self.adobe_tags and len(self.adobe_tags)>len(tags): tags = self.adobe_tags
        if self.shutter_tags and len(self.shutter_tags)>len(tags): tags = self.shutter_tags
        if self.google_tags and len(self.google_tags)>len(tags): tags = self.google_tags
        if self.aws_tags and len(self.aws_tags)>len(tags): tags = self.aws_tags

        tags = tags.split(',')
        tags = ['#'+n.replace(' ','') for n in tags]
        random.shuffle(tags)
        tags.sort(key=str.lower)
        if 'DJI' in self.name:
            tags = tags[:29]
            tags.append('#dronephotography')
        else:
            tags = tags[:30]

        tags = ' '.join(tags)
        return mark_safe('<div><span class="copy_tags">'+
            str(self.title or '') + '\n' + tags + '\n' + self.name + 
            '</span> <a href="#" class="copy_tags">(^C)</a></div>')

    instagram_text.short_description = 'instagram_text'

    def get_mykeywords(self):
        username=os.environ['MYKEYWORDER_USERNAME']
        key=os.environ['MYKEYWORDER_KEY']

        print(username,key)

        response = requests.get(f'http://mykeyworder.com/api/v1/analyze?url={self.url}?tr=w:600',auth=(username,key))

        print(response)
        print(response.text)

        res = response.json()
        print (res)
        print (res['keywords'])
        kw = ','.join(res['keywords'])
        return kw

    def get_imagekit_kw(self,provider='google'):
        imagekit = ImageKit(
            private_key=os.environ['IMAGEKIT_PRIVATE_KEY'],
            public_key=os.environ['IMAGEKIT_PUBLIC_KEY'],
            url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT'],
        )

        res = imagekit.list_files({'path':os.path.dirname(self.path),'name':self.name})
        print(res)

        if not res['error'] and res['response']:
            id = res['response'][0]['fileId']

        if id and res['response'][0]['AITags']:
            tags = []
            for tag in res['response'][0]['AITags']:
                if tag['source']==f"{provider}-auto-tagging":
                    print (tag)
                    tags.append(tag['name'])

            if tags:
                return ','.join(tags)

        updated_detail = imagekit.update_file_details(id,
            {"extensions": [
                {
                    "name": f"{provider}-auto-tagging",
                    "maxTags": 25,
                    "minConfidence": 50
                },
            ]}
        )

        print("Updated detail-", updated_detail, end="\n\n")

        if not updated_detail['error'] and updated_detail['response'] and updated_detail['response']['AITags']:
            tags = []
            for tag in updated_detail['response']['AITags']:
                if tag['source']==f"{provider}-auto-tagging":
                    print (tag)
                    tags.append(tag['name'])

            if tags:
                return ','.join(tags)

        res = imagekit.list_files({'path':os.path.dirname(self.path),'name':self.name})
        print(res)
        if not res['error'] and res['response'] and res['response'][0]['AITags']:
            tags = []
            for tag in res['response'][0]['AITags']:
                if tag['source']==f"{provider}-auto-tagging":
                    print (tag)
                    tags.append(tag['name'])

            if tags:
                return ','.join(tags)

        return ''


class Album(models.Model):
    path = models.CharField('path',max_length=200, unique=True)
    no_show = models.BooleanField('no show',default=False)
    created_dt = models.DateTimeField('created_dt',auto_now_add=True, null=True)
    updated_dt = models.DateTimeField('updated_dt',auto_now=True, null=True)
    title = models.CharField('title',max_length=100,null=True, blank=True,)
    slug = models.CharField('slug',max_length=100,null=False, blank=True, unique=True, )
    description = models.TextField('description',null=True, blank=True,)
    position = models.IntegerField('position',default=0, blank=True,)
    cover = models.CharField('cover',max_length=200,blank=True,default='')
    level = models.IntegerField('level',default=0, )

    def __str__(self):
        return str(self.id) + ':' + str(self.title)

    def img_tag(self):
        return mark_safe('<img src="%s" width="600" />' % (self.cover + '?tr=w-600'))

    img_tag.short_description = 'Image'

    def thumb_tag(self):
        return mark_safe('<img src="%s" width="250" alt="image" />' % (self.cover + '?tr=w-250'))

    thumb_tag.short_description = 'thumb'

    def save(self, *args, **kwargs):

        if self.path:
            self.level = self.path.count('/') - 3
        else:
            self.level = -1
            self.no_show = True

        if not self.slug:
            self.slug = slugify(self.title)

            
        super().save(*args, **kwargs)

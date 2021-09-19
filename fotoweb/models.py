from django.db import models
from django.utils.html import mark_safe

# Create your models here.
class Image(models.Model):
    name = models.CharField('name',max_length=100, unique=True)
    path = models.CharField('path',max_length=200, unique=True)
    url = models.CharField('url',max_length=200, unique=True)
    created_dt = models.DateTimeField('created_dt',auto_now_add=True, null=True)
    updated_dt = models.DateTimeField('created_dt',auto_now=True, null=True)
    mykeyworder_tags = models.TextField('mykeyworder tags',null=True, blank=True)
    adobe_tags = models.TextField('adobe tags',null=True, blank=True,)
    google_tags = models.TextField('goggle tags',null=True, blank=True,)
    title = models.CharField('title',max_length=100)
    description = models.TextField('description',null=True, blank=True,)
    tags = models.TextField('tags',null=True, blank=True,)
    instagram = models.BooleanField('instagram',default=False)
    instagram_dt = models.DateTimeField('instagram_dt',null=True, blank=True,)
    instagram_code = models.CharField('instagram_code',null=True, blank=True,max_length=20)
    adobe = models.BooleanField('adobe',default=False)
    adobe_dt = models.DateTimeField('adobe_dt',null=True, blank=True,)
    shutter = models.BooleanField('shutter',default=False)
    shutter_dt = models.DateTimeField('shutter_dt',null=True, blank=True,)

    def __str__(self):
        return str(self.id) + ':' + str(self.name)

    def img_tag(self):
        return mark_safe('<img src="%s" width="250" height="250" />' % (self.url))

    img_tag.short_description = 'Image'

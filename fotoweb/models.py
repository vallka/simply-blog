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
    shutter_tags = models.TextField('shutter tags',null=True, blank=True,)
    title = models.CharField('title',max_length=100,null=True, blank=True,)
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


    def __str__(self):
        return str(self.id) + ':' + str(self.name)

    def img_tag(self):
        return mark_safe('<img src="%s" width="600" />' % (self.url + '?tr=w-600'))

    img_tag.short_description = 'Image'

    def thumb_tag(self):
        return mark_safe('<img src="%s" width="250" alt="image" />' % (self.url + '?tr=w-250'))

    thumb_tag.short_description = 'thumb'

    def instagram_text(self):
        #tags = self.tags or self.mykeyworder_tags or self.adobe_tags or self.shutter_tags or self.google_tags or ''
        tags = ''
        if self.tags and len(self.tags)>len(tags): tags = self.tags
        if self.mykeyworder_tags and len(self.mykeyworder_tags)>len(tags): tags = self.mykeyworder_tags
        if self.adobe_tags and len(self.adobe_tags)>len(tags): tags = self.adobe_tags
        if self.shutter_tags and len(self.shutter_tags)>len(tags): tags = self.shutter_tags
        if self.google_tags and len(self.google_tags)>len(tags): tags = self.google_tags

        tags = tags.split(',')
        tags = ['#'+n.replace(' ','') for n in tags]
        if 'DJI' in self.name:
            tags = tags[:29]
            tags.append('#dronephotography')
        else:
            tags = tags[:30]

        tags = ' '.join(tags)
        return str(self.title or '') + '\n' + tags + '\n' + self.name

    instagram_text.short_description = 'instagram_text'


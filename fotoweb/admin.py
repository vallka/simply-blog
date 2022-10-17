import os
import re
import random
from datetime import datetime

from django.db.models import Q
from django.contrib import admin
from .models import *

from django.conf import settings


# Register your models here.
#admin.site.register(Image)

@admin.action(description='Mark selected as Instagrammed')
def make_published_insta(modeladmin, request, queryset):
    queryset.filter(instagram=False).update(instagram=True)
    queryset.filter(instagram_dt__isnull=True).update(instagram_dt=datetime.now())

@admin.action(description='Mark selected as Abobed')
def make_published_adobe(modeladmin, request, queryset):
    queryset.filter(adobe=False).update(adobe=True)
    queryset.filter(adobe_dt__isnull=True).update(adobe_dt=datetime.now())

@admin.action(description='Mark selected as Shutterstocked')
def make_published_shutter(modeladmin, request, queryset):
    queryset.filter(shutter=False).update(shutter=True)
    queryset.filter(shutter_dt__isnull=True).update(shutter_dt=datetime.now())

@admin.action(description='Mark selected as Pexelled')
def make_published_pexels(modeladmin, request, queryset):
    queryset.filter(pexels=False).update(pexels=True)
    queryset.filter(pexels_dt__isnull=True).update(pexels_dt=datetime.now())

@admin.action(description='Mark selected as Rasfocused')
def make_published_rasfocus(modeladmin, request, queryset):
    queryset.filter(rasfocus=False).update(rasfocus=True)
    queryset.filter(rasfocus_dt__isnull=True).update(rasfocus_dt=datetime.now())

@admin.action(description='Make CSV for Shutterstock')
def make_csv_shutter(modeladmin, request, queryset):
    csv = "Filename,Description,Keywords,Categories,Editorial\n"

    for q in queryset:
        desc = q.description or q.title
        editorial = 'yes' if q.editorial else 'no'
        csv +=  f'"{q.name}","{desc}","{q.tags}","{q.shutter_cat1},{q.shutter_cat2}","{editorial}"\n'

    print (csv)    
    
    with open(os.path.join(settings.MEDIA_ROOT, 'shutterstock.csv'), 'w') as writer:
        writer.write(csv)

@admin.action(description='Make CSV for Adobe')
def make_csv_adobe(modeladmin, request, queryset):
    csv = "Filename,Title,Keywords,Category\n"

    for q in queryset:
        desc = q.description or q.title
        adobe_cat = 11 #landscapes
        csv +=  f'"{q.name}","{desc}","{q.tags}","{adobe_cat}"\n'

    print (csv)    
    
    with open(os.path.join(settings.MEDIA_ROOT, 'adobe.csv'), 'w') as writer:
        writer.write(csv)

@admin.action(description='Get Mykeyworder tags')
def get_mykeyworder_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.mykeyworder_tags = q.get_mykeywords()
        q.add_auto_tags(q.mykeyworder_tags)
        q.add_auto_title(q.mykeyworder_tags)
        q.save()

@admin.action(description='Get Google tags')
def get_google_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.google_tags = q.get_imagekit_kw()
        q.add_auto_tags(q.google_tags)
        q.add_auto_title(q.google_tags)
        q.save()

@admin.action(description='Get AWS tags')
def get_aws_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.aws_tags = q.get_imagekit_kw('aws')
        q.add_auto_tags(q.aws_tags)
        q.add_auto_title(q.aws_tags)
        q.save()

@admin.register(Image)
class GellifinstaAdmin(admin.ModelAdmin):
    actions = [make_csv_shutter,
            make_csv_adobe,
            make_published_insta,
            make_published_adobe,
            make_published_shutter,
            make_published_pexels,
            make_published_rasfocus,
            get_mykeyworder_tags,get_google_tags,get_aws_tags]

    list_display = ['thumb_tag','id','path','tags_spaced','instagram_text','instagram','adobe','shutter','pexels','rasfocus']
    list_display_links = ['id','path','thumb_tag',]
    list_filter = ['instagram','adobe','shutter','pexels','rasfocus']
    search_fields = ['path','title','id']
    date_hierarchy = 'created_dt'

    readonly_fields = ['img_tag','url','created_dt','updated_dt']
    fields = [
            'name',
            'path',
            'url',
            'img_tag',
            'title',
            'description',
            'no_show',
            'private',
            'editorial',
            'tags',
            'mykeyworder_tags',
            'adobe_tags',
            'google_tags',
            'aws_tags',
            'shutter_tags',
            'shutter_cat1',
            'shutter_cat2',
            'instagram',
            'instagram_dt',
            'instagram_code',
            'adobe',
            'adobe_dt',
            'shutter',
            'shutter_dt',
            'shutter_url',
            'pexels',
            'pexels_dt',
            'pexels_url',
            'rasfocus',
            'rasfocus_dt',
            'rasfocus_url',
            'created_dt',
            'updated_dt',
    ]

    def img_tag(self,instance):
        return mark_safe('<img src="%s" width="625" />' % (instance.url + '?tr=w-625'))

    img_tag.short_description = 'Image'

    def thumb_tag(self,instance):
        return mark_safe('<img src="%s" width="250" alt="image" />' % (instance.url + '?tr=w-250'))

    thumb_tag.short_description = 'thumb'

    def instagram_text(self,instance):
        #tags = self.tags or self.mykeyworder_tags or self.adobe_tags or self.shutter_tags or self.google_tags or ''
        tags = ''
        if instance.tags and len(instance.tags)>len(tags): tags = instance.tags
        if instance.mykeyworder_tags and len(instance.mykeyworder_tags)>len(tags): tags = instance.mykeyworder_tags
        if instance.adobe_tags and len(instance.adobe_tags)>len(tags): tags = instance.adobe_tags
        if instance.shutter_tags and len(instance.shutter_tags)>len(tags): tags = instance.shutter_tags
        if instance.google_tags and len(instance.google_tags)>len(tags): tags = instance.google_tags
        if instance.aws_tags and len(instance.aws_tags)>len(tags): tags = instance.aws_tags

        tags = tags.split(',')
        tags = ['#'+n.replace(' ','') for n in tags]
        random.shuffle(tags)
        if 'DJI' in instance.name:
            tags = tags[:29]
            tags.append('#dronephotography')
        else:
            tags = tags[:30]

        tags.sort(key=str.lower)
        tags = ' '.join(tags)

        return mark_safe('<div><span class="copy_tags">'+
            str(instance.title or '') + '\n' + tags + '\n' + instance.name + 
            '</span> <a href="#" class="copy_tags">(^C)</a></div>')

    instagram_text.short_description = 'instagram_text'

    def tags_spaced(self,instance):
        tags = ''
        if instance.tags and len(instance.tags)>len(tags): tags = instance.tags
        if instance.mykeyworder_tags and len(instance.mykeyworder_tags)>len(tags): tags = instance.mykeyworder_tags
        if instance.adobe_tags and len(instance.adobe_tags)>len(tags): tags = instance.adobe_tags
        if instance.shutter_tags and len(instance.shutter_tags)>len(tags): tags = instance.shutter_tags
        if instance.google_tags and len(instance.google_tags)>len(tags): tags = instance.google_tags
        if instance.aws_tags and len(instance.aws_tags)>len(tags): tags = instance.aws_tags
        return mark_safe('<div><span class="copy_tags">'+tags.replace(',',', ') + '</span> <a href="#" class="copy_tags">(^C)</a></div>')

    tags_spaced.short_description = 'Tags'


    def get_search_results(self, request, queryset, search_term):

        if not search_term:
            queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
            return queryset, may_have_duplicates

        if search_term[0:2]=='a:':
            album_id = search_term[2:]
            queryset, may_have_duplicates = super().get_search_results(request, queryset, '')
            try:
                if re.match(r'^\d+$',album_id):
                    album = Album.objects.get(id=int(album_id))
                else:    
                    album = Album.objects.get(slug=album_id)
                new_album = album.path
                new_album = new_album.replace(' ','_')
                new_album = re.sub(r'[^/_0-9A-Za-z\-.]','_',new_album)
                new_album = new_album.replace('__','_')
                print('album:',album,new_album)

            except Album.DoesNotExist:    
                new_album = '///////'

            queryset3 = Image.objects.filter(path__icontains=new_album)

            print(len(queryset3),len(queryset))

            return queryset & queryset3, may_have_duplicates


        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)

        sql = "SELECT id from fotoweb_image"
        sql += " where match(name,path,mykeyworder_tags,adobe_tags,google_tags,aws_tags,shutter_tags,title,description,tags) against (%s in boolean mode) limit 0,1000"

        queryset2 = self.model.objects.raw(sql,[search_term])

        print( len(queryset2),len(queryset))
        if len(queryset2)>0:
            s=[]
            for row in queryset2:
                s.append(row.id)

            queryset3 = self.model.objects.filter(id__in=s)
            return queryset & queryset3, may_have_duplicates

        return queryset, may_have_duplicates    


@admin.register(Album)
class GellifinstaAlbumAdmin(admin.ModelAdmin):
    list_display = ['thumb_tag','title','position','id',]
    list_display_links = list_display
    search_fields = ['path','title',]

    readonly_fields = ['img_tag','created_dt','updated_dt']

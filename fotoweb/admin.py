import os
import re
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
    list_display = ['thumb_tag','id','path','tags_spaced','instagram_text','instagram','adobe','shutter','pexels','rasfocus']
    list_display_links = ['id','path','thumb_tag',]
    list_filter = ['instagram','adobe','shutter','pexels','rasfocus']
    search_fields = ['path','title','id']

    readonly_fields = ['img_tag','url','created_dt','updated_dt']
    actions = [make_csv_shutter,
            make_published_insta,
            make_published_adobe,
            make_published_shutter,
            make_published_pexels,
            make_published_rasfocus,
            get_mykeyworder_tags,get_google_tags,get_aws_tags]

    def get_search_results(self, request, queryset, search_term):
        if search_term[0:2]=='a:':
            album_id = search_term[2:]
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

            r = Image.objects.filter(path__icontains=new_album)
            return r, False    

        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)

        sql = "SELECT id from fotoweb_image"
        sql += " where match(name,path,mykeyworder_tags,adobe_tags,google_tags,aws_tags,shutter_tags,title,description,tags) against (%s in boolean mode) limit 0,100"

        queryset2 = self.model.objects.raw(sql,[search_term])

        print( len(queryset2))
        if len(queryset2)>0:
            s=[]
            for row in queryset2:
                s.append(row.id)

            queryset3 = self.model.objects.filter(id__in=s)
            return queryset | queryset3, may_have_duplicates

        return queryset, may_have_duplicates    


@admin.register(Album)
class GellifinstaAlbumAdmin(admin.ModelAdmin):
    list_display = ['thumb_tag','title','position','id',]
    list_display_links = list_display
    search_fields = ['path','title',]

    readonly_fields = ['img_tag','created_dt','updated_dt']

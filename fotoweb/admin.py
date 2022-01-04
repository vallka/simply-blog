import os

from django.contrib import admin
from .models import *

from django.conf import settings


# Register your models here.
#admin.site.register(Image)

@admin.action(description='Mark selected as Instagrammed')
def make_published_insta(modeladmin, request, queryset):
    queryset.update(instagram=True)

@admin.action(description='Mark selected as Abobed')
def make_published_adobe(modeladmin, request, queryset):
    queryset.update(adobe=True)

@admin.action(description='Mark selected as Shutterstocked')
def make_published_shutter(modeladmin, request, queryset):
    queryset.update(shutter=True)

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
        q.save()

@admin.action(description='Get Google tags')
def get_google_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.google_tags = q.get_imagekit_kw()
        q.save()

@admin.action(description='Get AWS tags')
def get_aws_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.aws_tags = q.get_imagekit_kw('aws')
        q.save()

@admin.register(Image)
class GellifinstaAdmin(admin.ModelAdmin):
    list_display = ['id','path','thumb_tag','instagram_text','instagram','adobe','shutter']
    list_display_links = ['id','path','thumb_tag']
    list_filter = ['instagram','adobe','shutter']
    search_fields = ['path','title','id']

    readonly_fields = ['img_tag','url','created_dt','updated_dt']
    actions = [make_csv_shutter,make_published_insta,make_published_adobe,make_published_shutter,get_mykeyworder_tags,get_google_tags,get_aws_tags]

@admin.register(Album)
class GellifinstaAlbumAdmin(admin.ModelAdmin):
    list_display = ['id','path','title','position','thumb_tag',]
    list_display_links = ['id','path','title','position','thumb_tag']
    search_fields = ['path','title',]

    readonly_fields = ['img_tag','created_dt','updated_dt']

from django.contrib import admin
from .models import *

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

@admin.register(Image)
class GellifinstaAdmin(admin.ModelAdmin):
    list_display = ['id','path','thumb_tag','instagram_text','instagram','adobe','shutter']
    list_display_links = ['id','path','thumb_tag']
    list_filter = ['instagram','adobe','shutter']
    search_fields = ['path','title',]

    readonly_fields = ['img_tag','url']
    actions = [make_published_insta,make_published_adobe,make_published_shutter]
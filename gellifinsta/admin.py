from django.contrib import admin
from .models import *

# Register your models here.

#admin.site.register(Gellifinsta)
#admin.site.register(Products)
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ['name','is_active']
    search_fields = ['name','is_active', ]

@admin.register(Gellifinsta)
class GellifinstaAdmin(admin.ModelAdmin):
    list_display = ['shortcode','taken_at_datetime','is_video','image_tag',]
    search_fields = ['caption','tags', ]
    #list_filter = ['tags',]
    fields = ['shortcode','taken_at_datetime','created_dt','updated_dt','username','is_active','is_video',
                'file_path','caption','tags','url','image_tag']

    readonly_fields = ['image_tag','created_dt','updated_dt']
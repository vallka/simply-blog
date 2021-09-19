from django.contrib import admin
from .models import *

# Register your models here.
#admin.site.register(Image)

@admin.register(Image)
class GellifinstaAdmin(admin.ModelAdmin):
    list_display = ['id','name','path','thumb_tag',]

    readonly_fields = ['img_tag','name','path','url']
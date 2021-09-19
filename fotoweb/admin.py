from django.contrib import admin
from .models import *

# Register your models here.
#admin.site.register(Image)

@admin.register(Image)
class GellifinstaAdmin(admin.ModelAdmin):
    list_display = ['id','name','path','img_tag',]
    fields = '__all__'

    readonly_fields = ['img_tag','name','path','url']
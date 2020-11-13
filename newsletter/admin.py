from django.contrib import admin
from .models import *

# Register your models here.
# Register your models here.
#admin.site.register(NewsShot)

@admin.register(NewsShot)
class NewsShotAdmin(admin.ModelAdmin):
    list_display = ['id','uuid','blog','customer_id','sent_dt','received_dt','opened_dt','clicked_dt','clicked_qnt']
    list_filter = ['blog',]
    #search_fields = ['title','text', ]

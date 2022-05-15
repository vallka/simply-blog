from django.contrib import admin

# Register your models here.
from .models import Castle

#admin.site.register(Castle)

@admin.register(Castle)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id','name','grid_reference',]
    search_fields = ['name','description_short', 'closest_to']

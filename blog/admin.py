from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from markdownx.models import MarkdownxField
from django.db import models
from django.forms.widgets import Textarea

from .models import *

# Register your models here.
#admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(Category)

@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    list_display = ['id','slug','title','blog','email','created_dt']
    search_fields = ['title','text', ]

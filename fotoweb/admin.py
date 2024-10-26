import json
import os
import re
import random
from datetime import datetime
from django.shortcuts import HttpResponseRedirect, render
import pytz
import csv
from icecream import ic

from django.db.models import Q
from django.contrib import admin
from .models import *

from django.conf import settings

from django.http import HttpResponse
from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget

class ImageModelAdminForm(forms.ModelForm):
    title = forms.CharField(widget=AdminTextareaWidget(attrs={'rows': 3}))

    class Meta:
        model = Image
        fields = '__all__'


# Register your models here.
#admin.site.register(Image)

@admin.action(description='Set selected as No Show')
def set_no_show(modeladmin, request, queryset):
    queryset.filter(no_show=False).update(no_show=True)

@admin.action(description='Set selected as Show')
def set_show(modeladmin, request, queryset):
    queryset.filter(no_show=True).update(no_show=False)

@admin.action(description='Set selected as Private')
def set_private(modeladmin, request, queryset):
    queryset.filter(private=False).update(private=True)

@admin.action(description='Set selected as non Private')
def set_non_private(modeladmin, request, queryset):
    queryset.filter(private=True).update(private=False)

@admin.action(description='Mark selected as Abobed')
def make_published_adobe(modeladmin, request, queryset):
    queryset.filter(adobe=False).update(adobe=True)
    queryset.filter(adobe_dt__isnull=True).update(adobe_dt=datetime.now(pytz.timezone('Europe/London')))

@admin.action(description='Mark selected as Shutterstocked')
def make_published_shutter(modeladmin, request, queryset):
    queryset.filter(shutter=False).update(shutter=True)
    queryset.filter(shutter_dt__isnull=True).update(shutter_dt=datetime.now(pytz.timezone('Europe/London')))
    modeladmin.message_user(request,"Changed status on {} images".format(queryset.count()))

@admin.action(description='Mark selected as Pexelled')
def make_published_pexels(modeladmin, request, queryset):
    queryset.filter(pexels=False).update(pexels=True)
    queryset.filter(pexels_dt__isnull=True).update(pexels_dt=datetime.now(pytz.timezone('Europe/London')))

@admin.action(description='Mark selected as Rasfocused')
def make_published_rasfocus(modeladmin, request, queryset):
    queryset.filter(rasfocus=False).update(rasfocus=True)
    queryset.filter(rasfocus_dt__isnull=True).update(rasfocus_dt=datetime.now(pytz.timezone('Europe/London')))

@admin.action(description='Make CSV for Shutterstock')
def make_csv_shutter(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shutterstock_' + datetime.now().strftime("%y%m%d%H%M%S") + '.csv"'

    writer = csv.writer(response)
    writer.writerow(["Filename","Description","Keywords","Categories","Editorial",])
    for q in queryset:
        desc = q.title
        editorial = 'yes' if q.editorial else 'no'

        writer.writerow([q.name,desc,q.tags,f'{q.shutter_cat1}, {q.shutter_cat2}',editorial,])
    
    return response

@admin.action(description='Make CSV for Adobe')
def make_csv_adobe(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="adobe_' + datetime.now().strftime("%y%m%d%H%M%S") + '.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Filename","Title","Keywords","Category",])
    for q in queryset:
        desc = q.title
        adobe_cat = 11 #landscapes
        writer.writerow([q.name,desc,q.tags,adobe_cat])
    
    return response

@admin.action(description='Get Mykeyworder tags')
def get_mykeyworder_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.mykeyworder_tags = q.get_mykeywords()
        q.add_auto_tags(q.mykeyworder_tags)
        #q.add_auto_title(q.mykeyworder_tags)
        q.save()

@admin.action(description='Get Google tags')
def get_google_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.google_tags = q.get_imagekit_kw()
        q.add_auto_tags(q.google_tags)
        #q.add_auto_title(q.google_tags)
        q.save()

@admin.action(description='Get AWS tags')
def get_aws_tags(modeladmin, request, queryset):
    for q in queryset:
        print (q.url)
        q.aws_tags = q.get_imagekit_kw('aws')
        q.add_auto_tags(q.aws_tags)
        #q.add_auto_title(q.aws_tags)
        q.save()

@admin.action(description='Get Scenex Titles')
def get_scenex_titles(modeladmin, request, queryset):
    i = 0
    imgs=[]
    for q in queryset:
        imgs.append({'id':q.id,'url':q.url + '?tr=w-600','title':q.title})
        i+=1
        print (i,i%8,q.url + '?tr=w-600')
        if i%8==0:
            call_scenex(imgs)
            ic(imgs)
            for img in imgs:
                q = Image.objects.get(id=img['id'])
                q.title = img['title']
                q.save()
            imgs=[]

        #q.aws_tags = q.get_imagekit_kw('aws')
        #q.add_auto_tags(q.aws_tags)
        #q.save()
    
    if imgs:
        call_scenex(imgs)
        ic(imgs)
        for img in imgs:
            q = Image.objects.get(id=img['id'])
            q.title = img['title']
            q.save()
        imgs=[]


def call_scenex(imgs):
    api_key = os.getenv('SCENEX_KEY')
    headers = {
        'Content-Type': 'application/json',
        "x-api-key": f"token {api_key}",
    }    

    data = []
    for img in imgs:
        ic(img)
        data.append(            {
                    'image': img['url'], 
                    'features': ['opt_out'],
                    'algorithm': 'Comet',
                    'languages': ['en'],
                    'style': 'concise',
                    'output_length': 199 - (len(img['title']) if img['title'] else 0)
                },
        )

    ic ({'data':data})
    responseobj = requests.post('https://api.scenex.jina.ai/v1/describe', headers=headers, data=json.dumps({'data':data}))
    ic(responseobj)

    response = responseobj.text
    ic(response)
    response = json.loads(responseobj.text)

    for index,img in enumerate(imgs):
        if not img['title']: img['title'] = ''
        if img['title'] and not img['title'][-1] in ['.',',','!','?']:
            img['title'] += '.'
        
        if img['title'] and not img['title'][-1]==' ':
            img['title'] += ' '

        img['title'] = truncate_string(img['title'] + response['result'][index]['text'],200-len(img['title']))


def truncate_string(string, max_length):
    if len(string) <= max_length:
        return string
    
    punctuations = ['.', '!', '?']
    truncated_string = string[:max_length]
    
    last_punctuation_index = -1
    
    for i in range(max_length-1, -1, -1):
        if truncated_string[i] in punctuations:
            last_punctuation_index = i
            break

    if last_punctuation_index != -1:
        truncated_string = truncated_string[:last_punctuation_index+1]
        return truncated_string


    for i in range(max_length-1, -1, -1):
        if truncated_string[i] == ' ':
            last_punctuation_index = i
            truncated_string = truncated_string[:i] + '.'
            break
    
    if last_punctuation_index != -1:
        truncated_string = truncated_string[:last_punctuation_index+1]
    
    return truncated_string


@admin.action(description='Get ChatGPT Titles')
def get_chatgpt_titles(modeladmin, request, queryset):
    for q in queryset:
        ic(q.tags)
        ic(q.url + '?tr=w-600')

        r = chatgpt_titles(q.tags,q.url + '?tr=w-512')
        ic(r)
        q.add_auto_tags(r["keywords"])
        q.title = r["title"]
        q.save()



#@admin.register(Image,ImageModelAdminForm)
class GellifinstaAdmin(admin.ModelAdmin):
    form = ImageModelAdminForm
    def update_title(self, request, queryset):
        if 'apply' in request.POST and 'title' in request.POST and request.POST['title'].strip(' ')!='':
            queryset.update(title=request.POST['title'].strip(' '))
            self.message_user(request,"Updated Title on {} images".format(queryset.count()))
            return
            
        return render(request,'admin/fotoweb/update_title.html',context={'items':queryset})
    update_title.short_description = 'Update Title'

    def update_tags(self, request, queryset):
        if 'apply' in request.POST and 'tags' in request.POST and request.POST['tags'].strip(' ')!='':
            #queryset.update(tags=request.POST['tags'].strip(' '))
            for q in queryset:
                q.add_auto_tags(request.POST['tags'].strip(' '))
                q.save()
            self.message_user(request,"Updated Tags on {} images".format(queryset.count()))
            return
            
        return render(request,'admin/fotoweb/update_tags.html',context={'items':queryset})
    update_tags.short_description = 'Update Tags'

    @admin.action(description='Mark selected as Instagrammed')
    def make_published_insta(self, request, queryset):
        queryset.filter(instagram=Image.InstaStatus.NONE).update(instagram=Image.InstaStatus.POSTED)
        queryset.filter(instagram_dt__isnull=True).update(instagram_dt=datetime.now(pytz.timezone('Europe/London')))

    @admin.action(description='Mark selected as non Instagrammed')
    def make_published_not_insta(self, request, queryset):
        queryset.filter(instagram=Image.InstaStatus.POSTED).update(instagram=Image.InstaStatus.NONE)

    actions = [make_csv_shutter,
            make_csv_adobe,
            set_no_show,
            set_show,
            set_private,
            set_non_private,
            make_published_insta,
            make_published_not_insta,
            make_published_adobe,
            make_published_shutter,
            make_published_pexels,
            make_published_rasfocus,
            update_title,update_tags,
            get_mykeyworder_tags,get_google_tags,get_aws_tags,
            get_scenex_titles,
            get_chatgpt_titles
            ]

    list_display = ['thumb_tag','id','path','tags_spaced','description_f','instagram_text_wtags','no_show','private','instagram','adobe','shutter',]
    list_display_links = ['id','path','thumb_tag',]
    list_filter = ['no_show','private','instagram','adobe','shutter',]
    search_fields = ['path','title','id']
    date_hierarchy = 'created_dt'

    readonly_fields = ['domain','img_tag','url','url_fs','created_dt','updated_dt']
    fields = [
            'name',
            'path',
            'path_fs',
            'url',
            'url_fs',
            'domain',
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
        return mark_safe('<img src="%s" height="200" alt="image" />' % (instance.url + '?tr=w-300'))

    thumb_tag.short_description = 'thumb'

    def instagram_text_wtags(self,instance):
        return mark_safe('<div><span class="copy_tags">' + str(instance.instagram_text) + '</span></div>')

    instagram_text_wtags.short_description = 'instagram_text'

    def description_f(self,instance):
        return mark_safe('<div><span class="copy_description">' + str(instance.description) + '</span></div>')

    description_f.short_description = 'description'

    def tags_spaced(self,instance):
        tags = ''
        if instance.tags and len(instance.tags)>len(tags): tags = instance.tags
        if instance.mykeyworder_tags and len(instance.mykeyworder_tags)>len(tags): tags = instance.mykeyworder_tags
        if instance.adobe_tags and len(instance.adobe_tags)>len(tags): tags = instance.adobe_tags
        if instance.shutter_tags and len(instance.shutter_tags)>len(tags): tags = instance.shutter_tags
        if instance.google_tags and len(instance.google_tags)>len(tags): tags = instance.google_tags
        if instance.aws_tags and len(instance.aws_tags)>len(tags): tags = instance.aws_tags
        return mark_safe('<div><span class="copy_title"><b>'+str(instance.title or '') +'</b></span><br><span class="copy_tags">'+tags.replace(',',', ') + '</span></div>')

    tags_spaced.short_description = 'Tags'

    def get_search_results(self, request, queryset, search_term):
        print('get_search_results')

        if not search_term:
            queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
            return queryset, may_have_duplicates

        if search_term=='a:instagram':
            queryset, may_have_duplicates = super().get_search_results(request, queryset, '')
            queryset3 = Image.objects.filter(
                Q(instagram=0) &
                Q(no_show=0) &
                Q(private=0) &
                ~Q(title='') &
                ~Q(tags='') &
                ~Q(title__isnull=True) &
                ~Q(tags__isnull=True)
            )

            print(len(queryset3),len(queryset))

            return queryset & queryset3, may_have_duplicates

        if search_term[0:2]=='a:':
            album_id = search_term[2:]
            queryset, may_have_duplicates = super().get_search_results(request, queryset, '')
            try:
                if re.match(r'^\d+$',album_id):
                    album = Album.objects.get(id=int(album_id))
                else:    
                    album = Album.objects.get(slug=album_id)

                path1 = album.path
                path1 = path1.replace(' ','_')
                path1 = re.sub(r'[^/_0-9A-Za-z\-.]','_',path1)
                path1 = path1.replace('__','_')
                path2 = album.path
                path2 = path1.replace('_',' ')
                queryset3 = Image.objects.filter(Q(path__icontains=album.path) | Q(path__icontains=path1) | Q(path__icontains=path2))

            except Album.DoesNotExist:    
                new_path = '///////'
                queryset3 = Image.objects.filter(Q(path__icontains=new_path))


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

admin.site.register(Image,GellifinstaAdmin)

@admin.register(Album)
class GellifinstaAlbumAdmin(admin.ModelAdmin):
    list_display = ['thumb_tag','id','title','domain','no_show']
    list_display_links = list_display
    search_fields = ['path','title',]
    list_filter = ['no_show','domain',]

    readonly_fields = ['img_tag','created_dt','updated_dt']

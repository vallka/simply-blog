import re
from django.shortcuts import render,redirect
from django.views import generic
from .models import *


import logging
logger = logging.getLogger(__name__)

class ImageListView(generic.ListView):
    model = Image
    paginate_by = 200

    def get_queryset(self):
        album = self.kwargs.get('album')
        if album:
            album = Album.objects.get(slug=album)

            new_album = album.path
            new_album = new_album.replace(' ','_')
            new_album = re.sub(r'[^/_0-9A-Za-z\-.]','_',new_album)
            new_album = new_album.replace('__','_')
            print('album:',album,new_album)

            r= Image.objects.filter(no_show=0,path__icontains=new_album).order_by('name')
            print (len(r))

            self.breadcrumb = album.title
            self.album_id = album.id

            return r
        else:
            self.breadcrumb = ''
            self.album_id = None
            return Image.objects.filter(no_show=0).order_by('-name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['breadcrumb'] = self.breadcrumb
        context['album_id'] = self.album_id
        context['page_title'] = context['breadcrumb']
        return context        

class ImageSearchView(generic.ListView):
    model = Image
    paginate_by = 200

    def get_queryset(self):
        self.q = self.request.GET.get('q')

        sql = Image.objects.filter(no_show=0).query
        sql = re.sub('ORDER BY.*$','',str(sql))
        sql += "and match(name,path,mykeyworder_tags,adobe_tags,google_tags,aws_tags,shutter_tags,title,description,tags) against (%s in boolean mode)"
        print(sql)

        posts = Image.objects.raw(sql,[self.q])
        self.len = len(posts)
        return posts
        #return Image.objects.filter(no_show=0).order_by('-name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #context['post'] = context['post_list'] and context['post_list'][0]

        page = int(self.request.GET.get('page',1))
        context['q'] = self.q

        context['breadcrumb'] = f'Search: {self.q} ({self.len})' 
        context['page_title'] = context['breadcrumb']
        return context        


class AlbumListView(generic.ListView):
    model = Album
    paginate_by = 200

    def render_to_response(self,context):
        print ('render_to_response')
        print (self.object_list)
        if len(self.object_list):
            return super().render_to_response(context)

        return redirect('fotoweb:album-photos', self.kwargs.get('album')) 

    
    def get_queryset(self):
        album = self.kwargs.get('album')
        if album:
            album = Album.objects.get(slug=album)

            new_album = album.path
            new_album = new_album.replace(' ','_')
            new_album = re.sub(r'[^/_0-9A-Za-z\-.]','_',new_album)
            new_album = new_album.replace('__','_')
            print('album:',album,new_album)

            self.breadcrumb = album.title
            self.album_id = album.id

            albums = Album.objects.filter(no_show=0,level=album.level+1,path__icontains=new_album).order_by('position','-id')
            return albums

        self.breadcrumb = ''
        self.album_id = None
        return Album.objects.filter(no_show=0,level=0).order_by('position','-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['breadcrumb'] = self.breadcrumb
        context['album_id'] = self.album_id
        context['page_title'] = context['breadcrumb']
        return context        

def view_img(request):
    path=request.GET['p']
    print ('view_img',path)
    logger.error("view_img - path:%s",path)

    return redirect(path)

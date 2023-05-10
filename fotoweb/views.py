import re
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import generic
from django.forms.models import model_to_dict

from rest_framework.decorators import api_view
from rest_framework.response import Response

from icecream import ic
import openai

from .models import *


import logging
logger = logging.getLogger(__name__)
ic.configureOutput(includeContext=True,contextAbsPath=True,prefix='')

class ImageView(generic.DetailView):
    model = Image

    def get(self, request, *args, **kwargs):
        #ic (self.kwargs)

        if self.kwargs.get('name'): 
            self.object = self.model.objects.get(name=self.kwargs.get('name'))
        else:
            self.object = self.get_object()

        context = self.get_context_data(object=self.object)


        if self.kwargs.get('par')=='json': 
            return JsonResponse(model_to_dict(self.object))
        
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context        

class ImageListView(generic.ListView):
    model = Image
    paginate_by = 200

    def get_queryset(self):
        album = self.kwargs.get('album')
        if album:
            album = Album.objects.get(slug=album)

            #logger.error("ImageListView - album:%s  (logger)",album)
            logger.info(ic.format(album))

            new_album = album.path
            new_album = new_album.replace(' ','_')
            new_album = re.sub(r'[^/_0-9A-Za-z\-.]','_',new_album)
            new_album = new_album.replace('__','_')
            logger.info(ic.format(new_album))

            r= Image.objects.filter(no_show=0,path__icontains=new_album).order_by('name')
            logger.info(ic.format(len(r)))

            self.breadcrumb = album.title
            self.album_id = album.id

            logger.error(ic.format('done'))

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
        sql += " and match(name,path,mykeyworder_tags,adobe_tags,google_tags,aws_tags,shutter_tags,title,description,tags) against (%s in boolean mode)"
        logger.error(ic.format(sql))

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
        #ic ('ren#der_to_response')
        #ic (self.object_list)
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
            logger.error(ic.format('album:',album,new_album))

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
    logger.error(ic.format(path))

    return redirect(path)

@api_view(['POST'])
def findtags(request):
    img_name = request.data['name']
    img = Image.objects.get(name=img_name)
    tags = img.get_imagekit_kw()

    #ic (tags)
    return Response({'tags': tags})

@api_view(['POST'])
def maketitle(request):
    description = request.data['description']

    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": f"Shorten the image description below to fit into 150 chars, including spaces and punctuation:\n\n{description}"}
            ]
    )


    logger.error(resp)

    #ic (tags)
    return Response({'title': resp.choices[0].message.content})    

@api_view(['POST'])
def getdescription(request):
    url = request.data['url']


    ic (url)



    return Response({'url': url })    
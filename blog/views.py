import re
from django.utils import timezone
from django.views import generic
from django.contrib.sitemaps import Sitemap

from .models import *


class ListView(generic.ListView):
    model = Post
    paginate_by = 5
    
    def get_queryset(self):
        
        posts = Post.objects.filter(blog_start_dt__lte=timezone.now(),blog=True,)
        cat_slug = self.kwargs.get('slug')
        if cat_slug:
            cat = Category.objects.get(slug=cat_slug)
            print (cat)
            posts = posts.filter(category=cat)
        else:
            cat_ex = Category.objects.filter(category__startswith='_')
            posts = posts.exclude(category__in=cat_ex)

        self.request.session['category'] = cat_slug

        return posts.order_by('-blog_start_dt')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['post'] = context['post_list'] and context['post_list'][0]
        context['categories'] = Category.objects.all().order_by('id')

        page = int(self.request.GET.get('page',1))

        n = 0
        for p in context['post_list']:
            if n>0 or page>1:
                #print(p.text)
                pics = re.finditer(r'\!\[\]\(',p.text)

                pos = [pic.start() for pic in pics]

                print(p.slug,pos)

                if len(pos)>1 and pos[0]<100:
                    p.text = p.text[0:pos[1]]
                    p.read_more = True
                
                elif len(pos)>0 and pos[0]>=100:
                    p.text = p.text[0:pos[0]]
                    p.read_more = True

                else:
                    crs = re.finditer(r'\n',p.text)    
                    pos = [cr.start() for cr in crs]
                    if len(pos)>3:
                        p.text = p.text[0:pos[3]]
                        p.read_more = True

            n += 1

        context['breadcrumb'] = re.sub(r'[^\x00-\x7F]',' ', context['post'].title)
        context['page_title'] = context['breadcrumb']
        return context        

class PostView(generic.DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = re.sub(r'[^\x00-\x7F]',' ', context['post'].title)
        context['categories'] = Category.objects.all().order_by('id')

        this_dt = context['post'].blog_start_dt

        if this_dt:
            cat_slug = self.request.session.get('category')
            cat = None
            if cat_slug:
                cat = Category.objects.get(slug=cat_slug)
            
                next = Post.objects.filter(
                    blog_start_dt__lte=timezone.now(),blog=True,blog_start_dt__gt=this_dt,category=cat
                ).order_by('blog_start_dt')[:1]

                prev = Post.objects.filter(
                    blog_start_dt__lte=timezone.now(),blog=True,blog_start_dt__lt=this_dt,category=cat
                ).order_by('-blog_start_dt')[:1]

            else:
                next = Post.objects.filter(
                    blog_start_dt__lte=timezone.now(),blog=True,blog_start_dt__gt=this_dt,
                ).order_by('blog_start_dt')[:1]

                prev = Post.objects.filter(
                    blog_start_dt__lte=timezone.now(),blog=True,blog_start_dt__lt=this_dt,
                ).order_by('-blog_start_dt')[:1]

            if len(next): 
                context['next'] = next[0].slug
            if len(prev): 
                context['prev'] = prev[0].slug

        return context        

class SearchView(generic.ListView):
    model = Post
    paginate_by = 50
    template_name = "blog/post_search.html"
    
    def get_queryset(self):
        
        self.q = self.request.GET.get('q')

        #sql = Post.objects.filter(blog_start_dt__lte="'"+str(timezone.now())+"'",blog=True,).query
        sql = Post.objects.filter(blog=True,).query
        sql = re.sub('ORDER BY.*$','',str(sql))

        #posts = Post.objects.filter(blog_start_dt__lte=timezone.now(),blog=True,title__contains=q)

        # sql = "select * from blog_post where match(title,text) against (%s in boolean mode) and blog=1 and blog_start_dt<=%s"
        sql += "and match(title,text) against (%s in boolean mode) and blog_start_dt<=now()"
        print(sql)


        posts = Post.objects.raw(sql,[self.q])
        self.len = len(posts)
        return posts

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['post'] = context['post_list'] and context['post_list'][0]
        context['categories'] = Category.objects.all().order_by('id')

        page = int(self.request.GET.get('page',1))
        #q = self.request.GET.get('q')
        context['q'] = self.q

        for p in context['post_list']:
            pics = re.finditer(r'\!\[\]\(',p.text)

            pos = [pic.start() for pic in pics]

            print(p.slug,pos)

            if len(pos)>1 and pos[0]<100:
                p.text = p.text[0:pos[1]]
                p.read_more = True
            
            elif len(pos)>0 and pos[0]>=100:
                p.text = p.text[0:pos[0]]
                p.read_more = True

            else:
                crs = re.finditer(r'\n',p.text)    
                pos = [cr.start() for cr in crs]
                if len(pos)>3:
                    p.text = p.text[0:pos[3]]
                    p.read_more = True


        context['breadcrumb'] = f'Search: {self.q} ({self.len})' 
        context['page_title'] = context['breadcrumb']
        return context        


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        # Assuming you have a method to fetch episodes
        return Post.objects.filter(blog_start_dt__lte=timezone.now(),blog=True,)

    def lastmod(self, obj):
        # Assuming you have a date field for last modification
        return obj.updated_dt


from django.utils import timezone
from django.views import generic

from .models import *


class ListView(generic.ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(
            blog_start_dt__lte=timezone.now(),blog=True
        ).order_by('-blog_start_dt')[:5]


class PostView(generic.DetailView):
    model = Post


#class BlogListView(generic.ListView):
#    model = Page
#    template_name = 'pages/blog_list.html'

#    def get_queryset(self):
#        return Page.objects.filter(blog_post=True).order_by('-created_dt')[:10]

#class BlogDetailView(generic.DetailView):
#    model = Page
#    template_name = 'pages/blog_detail.html'


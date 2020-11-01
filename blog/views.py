import re
from django.utils import timezone
from django.views import generic

from .models import *


class ListView(generic.ListView):
    model = Post
    
    def get_queryset(self):
        return Post.objects.filter(
            blog_start_dt__lte=timezone.now(),blog=True
        ).order_by('-blog_start_dt')[:5]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['post'] = context['post_list'][0]

        context['breadcrumb'] = re.sub(r'[^\x00-\x7F]',' ', context['post'].title)
        return context        

class PostView(generic.DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['breadcrumb'] = re.sub(r'[^\x00-\x7F]',' ', context['post'].title)
        return context        




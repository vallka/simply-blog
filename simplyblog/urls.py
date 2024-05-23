"""simplyblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include, path, re_path
from django.conf import settings

from django.conf.urls.static import static 
from django.shortcuts import redirect
from django.contrib.sitemaps.views import sitemap

from blog.views import BlogPostSitemap

sitemaps = {
   'blog': BlogPostSitemap, 
}

urlpatterns = [
    #path('', lambda request: redirect('blog/')),
    path('', lambda request: redirect('photo/')),
    path('admin/', admin.site.urls),
    path('blog/newsletter/', include('newsletter.urls')),
    path('blog/', include('blog.urls')),
    path('photo/', include('fotoweb.urls')),
    path('mycovidash/', include('mycovidash.urls')),
    path('castles/', include('castles.urls')),
    path('weather/', include('weather.urls')),
    #path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns


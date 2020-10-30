from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


# Create your models here.
class Category(models.Model):
    class Meta:
        ordering = ['slug']

    category = models.CharField(_("Category"), blank=True, max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, max_length=100, blank=True, null=False)
    is_default = models.BooleanField(_("Default Category"),default=False)

    def __str__(self):
        return str(self.slug) + ' -- ' + str(self.category)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category)
            
        super().save(*args, **kwargs)

class Post(models.Model):
    class Meta:
        ordering = ['slug']

    title = models.CharField(_("Title"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, max_length=100, blank=True, null=False)

    blog = models.BooleanField(_("Publish to blog"),default=False)
    blog_start_dt = models.DateTimeField(_("Publish Date/Time"), blank=True, null=True)
    email = models.BooleanField(_("Send as newsletter"),default=False)
    email_end_dt = models.DateTimeField(_("Send Date/Time"), blank=True, null=True)

    category = models.ManyToManyField(Category, blank=True, null=True)

    text = MarkdownxField(_("Text"), blank=True, null=False)

    created_dt = models.DateTimeField(_("Created Date/Time"), auto_now_add=True, null=True)
    updated_dt = models.DateTimeField(_("Updated Date/Time"), auto_now=True, null=True)

    description  = models.TextField(_("Meta Description"), blank=True, null=False, default='')
    keywords  = models.TextField(_("Meta Keywords"), blank=True, null=False, default='')
    json_ld  = models.TextField(_("script ld+json"), blank=True, null=False, default='')


    @property
    def formatted_markdown(self):
        return markdownify(self.text)

    def __str__(self):
        return str(self.id) + ':'+ str(self.slug) + ' -- ' + str(self.title)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        super().save(*args, **kwargs)
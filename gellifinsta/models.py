from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe


# Create your models here.
class Gellifinsta(models.Model):
    class Meta:
        ordering = ['-taken_at_datetime']

    shortcode = models.CharField(_("Shortcode"), max_length=20)
    taken_at_datetime = models.DateTimeField(_("taken at"))
    username = models.CharField(_("Username"), max_length=100)
    is_active = models.BooleanField(_("Active"),default=True)
    is_video = models.BooleanField(_("Video"),default=False)
    file_path = models.CharField(_("File Path"), max_length=500)
    url = models.CharField(_("URL"), max_length=500)
    created_dt = models.DateTimeField(_("Created Date/Time"), auto_now_add=True, null=True)
    updated_dt = models.DateTimeField(_("Updated Date/Time"), auto_now=True, null=True)
    caption = models.TextField(_("Caption"), blank=True, null=True)
    tags = models.TextField(_("Tags"), blank=True, null=True)

    def __str__(self):
        return self.shortcode + ':' + str(self.taken_at_datetime)

    def image_tag(self):
        return mark_safe('<img src="%s" width="250" height="250" />' % (self.url))

    image_tag.short_description = 'Image'

class Products(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(_("Name"), max_length=100, unique=True)
    is_active = models.BooleanField(_("Active"),default=True)

    def __str__(self):
        return self.name

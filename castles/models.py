from django.db import models

# Create your models here.
class Castle(models.Model):
    source = models.CharField(max_length=100,db_index=True)
    source_url = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=100,db_index=True)
    description_short = models.CharField(max_length=1000, blank=True, null=True)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    canmore_url = models.CharField(max_length=200, blank=True, null=True)
    canmore_map = models.CharField(max_length=200, blank=True, null=True)
    grid_reference = models.CharField(max_length=20, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    closest_to = models.CharField(max_length=200)
    access = models.CharField(max_length=100)
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
        
    class Meta:
        ordering = ['name']

        


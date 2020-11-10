import uuid

from django.db import models

from blog.models import *

# Create your models here.
class NewsShot(models.Model):
    class Meta:
        ordering = ['-id']

    uuid = models.UUIDField(db_index=True, default=uuid.uuid1, editable=True,unique=True)
    blog = models.ForeignKey(Post,on_delete=models.CASCADE,)
    customer_id = models.IntegerField(db_index=True)
    send_dt = models.DateTimeField(blank=True, null=True)
    received_dt = models.DateTimeField(blank=True, null=True)
    opened_dt = models.DateTimeField(blank=True, null=True)
    clicked_dt = models.DateTimeField(blank=True, null=True)
    clicked_qnt = models.IntegerField(blank=True, null=True)

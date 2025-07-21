# Create your models here.
from django.db import models
from taggit.managers import TaggableManager
from shortuuid.django_fields import ShortUUIDField
from core.models import User, EncoderProfile

class EventVideo(models.Model):
    encoder = models.ForeignKey(EncoderProfile, on_delete=models.CASCADE, related_name='event_videos')
    eventId = ShortUUIDField(unique=True, length=10, max_length=21, prefix="event", alphabet="ABCDEF0123456789")
    title = models.CharField(max_length=255)
    link = models.URLField()
    description = models.TextField(blank=True, null=True)
    tags = TaggableManager()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
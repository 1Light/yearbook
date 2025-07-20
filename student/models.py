# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class RSVPToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    responded = models.BooleanField(default=False)
    response = models.CharField(
        max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], blank=True
    )

    def __str__(self):
        return f"{self.user.email} - RSVP"

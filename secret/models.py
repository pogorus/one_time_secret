from django.db import models


class Secret(models.Model):
    text = models.TextField()
    secret_phrase = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    time_to_live = models.IntegerField(null=True, blank=True)

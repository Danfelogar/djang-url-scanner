from django.db import models

# Create your models here.
class URL(models.Model):
    original_url = models.URLField(max_length=200)
    scanned_at = models.DateTimeField(auto_now_add=True)
    status = models.JSONField(null=True, blank=True)
    detection = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.original_url


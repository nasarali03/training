from django.db import models

# Create your models here.
class MediaFile(models.Model):
    video_file=models.FileField(upload_to='videos/')
    converted_video = models.FileField(upload_to='converted_videos/', null=True, blank=True)
    size = models.FloatField(null=True, blank=True)
    title =  models.CharField(max_length=255,blank=True)
    uploaded_at=models.DateTimeField(auto_now_add=True)
    
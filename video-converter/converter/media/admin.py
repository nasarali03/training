from django.contrib import admin
from .models import MediaFile

@admin.register(MediaFile)
class Media(admin.ModelAdmin):
    list_display = ('id', 'title', 'converted_video', 'uploaded_at')
    search_fields = ('title',)
    list_filter = ('uploaded_at',)
    
    
from rest_framework import serializers
from .models import MediaFile

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = '__all__'
        read_only_fields = ['title', 'size']

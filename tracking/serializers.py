from rest_framework import serializers
from .models import TrackingCode


class TrackingCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingCode
        fields = ['id', 'script_id', 'name', 'script_content', 'noscript_content', 'placement', 'order']

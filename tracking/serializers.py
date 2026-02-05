from rest_framework import serializers
from .models import TrackingCode


class TrackingCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingCode
        fields = ['script_content']

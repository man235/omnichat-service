from rest_framework import serializers
from sop_chat_service.app_connect.models import FanPage


class FanPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanPage
        fields = ['id', 'name', 'page_id', 'avatar_url', 'is_active', 'created_by', 'created_at', 'last_subscribe']

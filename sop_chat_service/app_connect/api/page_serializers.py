from rest_framework import serializers
from sop_chat_service.app_connect.models import FanPage


class FanPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanPage
        fields = ['id', 'name', 'page_id', 'avatar_url', 'is_active', 'created_by', 'created_at', 'last_subscribe', 'type']

    def create(self, validated_data: dict):
        return FanPage.objects.create(**validated_data) 
    
    def update(self, instance: FanPage, validated_data: dict):
        instance.name = validated_data.get('name')
        instance.page_id = validated_data.get('page_id')
        instance.access_token_page = validated_data.get('access_token_page')
        instance.refresh_token_page = validated_data.get('refresh_token_page')
        instance.avatar_url = validated_data.get('avatar_url')
        instance.is_active = validated_data.get('is_active')
        instance.created_by = validated_data.get('created_by')
        instance.type = validated_data.get('type')
        instance.last_subscribe = validated_data.get('last_subscribe')
        instance.save()
        return instance
from rest_framework import serializers
from sop_chat_service.app_connect.models import FanPage


class FanPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanPage
        fields = ['id', 'name', 'page_id', 'avatar_url', 'is_active', 'is_deleted', 'created_by', 'created_at', 'last_subscribe', 'type']

    def create(self, validated_data: dict):
        return FanPage.objects.create(**validated_data) 
    
    def update(self, instance: FanPage, validated_data: dict):
        instance.name = validated_data.get('name', instance.name)
        instance.page_id = validated_data.get('page_id', instance.page_id)
        instance.access_token_page = validated_data.get('access_token_page', instance.access_token_page)
        instance.refresh_token_page = validated_data.get('refresh_token_page', instance.refresh_token_page)
        instance.avatar_url = validated_data.get('avatar_url', instance.avatar_url)
        instance.is_active = validated_data.get('is_active', instance.is_active )
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.type = validated_data.get('type', instance.type)
        instance.last_subscribe = validated_data.get('last_subscribe', instance.last_subscribe)
        instance.save()
        return instance


class SettingChatZaloSerializer(serializers.Serializer):
    page_id = serializers.CharField(required=True)
    setting_chat = serializers.CharField(required=True)
    group_user = serializers.ListField(child=serializers.CharField(required=False), required=False)

from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message, FanPage, Room, UserApp


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['mid', 'type', 'url']

class GetMessageSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender', 'created_at']

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id).first()
        sz = AttachmentSerializer(attachments, many=False)
        return sz.data

class LastMessageSerializer(serializers.ModelSerializer):
    type_attachments = serializers.SerializerMethodField(source='get_type_attachments', read_only=True)

    class Meta:
        model = Message


class FanpageInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanPage
        fields = ['name', 'avatar_url']


class RoomMessageSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)
    unseen_message_count = serializers.SerializerMethodField(source='get_unseen_message_count', read_only=True)
    user_info = serializers.SerializerMethodField(source='get_user_info', read_only=True)
    fanpage = serializers.SerializerMethodField(source='get_fanpage', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date',
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'unseen_message_count', 'room_id', 'user_info', 'fanpage']

    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj).order_by('-id').first()
        sz = GetMessageSerializer(message)
        return sz.data

    def get_unseen_message_count(self, obj):
        count = Message.objects.filter(room_id=obj, is_seen__isnull=False).count()
        return count
    
    def get_user_info(self, obj):
        user_info = UserApp.objects.filter(external_id=obj.external_id).first()
        sz_user_info = UserInfoSerializer(user_info)
        return sz_user_info.data
    
    def get_fanpage(self, obj):
        fanpage_info = FanPage.objects.filter(id=obj.page_id.id).first()
        sz_fanpage_info = FanpageInfoSerializer(fanpage_info)
        return sz_fanpage_info.data


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApp
        fields = ['id', 'name', 'email', 'phone', 'avatar', 'gender']

class ResponseSearchMessageSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField(source='get_user_info', read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'user_id', 'external_id', 'name', 'type', 'note', 'approved_date', 'completed_date', 'conversation_id', 'created_at', 'room_id', 'user_info']

    def get_user_info(self, obj):
        user_info = UserApp.objects.filter(external_id=obj.external_id).first()
        sz_user_info = UserInfoSerializer(user_info)
        return sz_user_info.data

class SearchMessageSerializer(serializers.Serializer):
    search = serializers.CharField(required=False)

class SortMessageSerializer(serializers.Serializer):
    sort = serializers.CharField(required=False)
    filter = serializers.DictField(required=False)

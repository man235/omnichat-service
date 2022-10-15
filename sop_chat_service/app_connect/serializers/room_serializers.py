from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message, FanPage, Room, UserApp, Label
from django.db.models import Q


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'mid', 'type', 'url', 'name']
class ServiceSurveytSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'mid', 'name', 'value']
class GetMessageSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender', 'created_at', 'uuid']

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id)
        sz = AttachmentSerializer(attachments, many=True)
        return sz.data


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date',
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'room_id']

    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj, is_sender=False).order_by('-id').first()
        sz = GetMessageSerializer(message)
        return sz.data


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["name", "color"]


class FanpageInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanPage
        fields = ['name', 'avatar_url']


class RoomMessageSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)
    unseen_message_count = serializers.SerializerMethodField(source='get_unseen_message_count', read_only=True)
    user_info = serializers.SerializerMethodField(source='get_user_info', read_only=True)
    fanpage = serializers.SerializerMethodField(source='get_fanpage', read_only=True)
    label = serializers.SerializerMethodField(source='get_label', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date',
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'unseen_message_count', 'room_id', 'user_info', 'fanpage', 'label']

    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj).order_by('-id').first()
        sz = GetMessageSerializer(message)
        return sz.data

    def get_unseen_message_count(self, obj):
        count = Message.objects.filter(room_id=obj, is_seen__isnull=True).count()
        return count
    
    def get_user_info(self, obj):
        user_info = UserApp.objects.filter(external_id=obj.external_id).first()
        sz_user_info = UserInfoSerializer(user_info)
        return sz_user_info.data
    
    def get_fanpage(self, obj):
        if not obj.page_id:
            return None
        fanpage_info = FanPage.objects.filter(id=obj.page_id.id).first()
        sz_fanpage_info = FanpageInfoSerializer(fanpage_info)
        return sz_fanpage_info.data

    def get_label(self, obj):
        message = Label.objects.filter(room_id=obj)
        sz = LabelSerializer(message, many=True)
        return sz.data


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApp
        fields = ['id','external_id', 'name', 'email', 'phone', 'avatar', 'gender']

class ResponseSearchMessageSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField(source='get_user_info', read_only=True)
    fan_page_name = serializers.SerializerMethodField(source='get_fan_page_name', read_only=True)
    fan_page_avatar =serializers.SerializerMethodField(source='get_fan_page_avatar', read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'user_id',"fan_page_name","fan_page_avatar", 'external_id', 'name', 'type', 'note', 'approved_date', 'completed_date', 'conversation_id', 'created_at', 'room_id', 'user_info']

    def get_user_info(self, obj):
        if not obj:
            return None
        user_info = UserApp.objects.filter(external_id=obj.external_id).first()
        sz_user_info = UserInfoSerializer(user_info)
        return sz_user_info.data
    def get_fan_page_name(self,obj):
        if not obj.page_id:
            return None
        page = FanPage.objects.filter(id=obj.page_id.id).first()
        if not page:
            return None
        return page.name
    def get_fan_page_avatar(self,obj):
        if not obj.page_id:
            return None
        page = FanPage.objects.filter(id=obj.page_id.id).first()
        if not page:
            return None
        return page.avatar_url
    

class SearchMessageSerializer(serializers.Serializer):
    search = serializers.CharField(required=False)

class SortMessageSerializer(serializers.Serializer):
    sort = serializers.CharField(required=False)
    filter = serializers.DictField(required=False)


class GetCountAttachmentMessageSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender', 'created_at']

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id).first()
        sz = AttachmentSerializer(attachments, many=False)
        return sz.data


class CountAttachmentRoomSerializer(serializers.ModelSerializer):
    message_attachment = serializers.SerializerMethodField(source='get_message_attachment', read_only=True)

    class Meta:
        model = Room
        fields = ['external_id', 'name', 'type', 'note','message_attachment']

    def get_message_attachment(self, obj):
        message_attachment = Message.objects.filter(room_id=obj)
        file_data = []
        image_data = []
        for message in message_attachment:
            attachment = Attachment.objects.filter(mid=message.id)
            sz_attachment = AttachmentSerializer(attachment, many=True)
            for attachment in sz_attachment.data:
                if 'image' in attachment['type'] or 'video' in attachment['type']:
                    image_data.append(attachment)
                else:
                    file_data.append(attachment)
        data = {
            "file_data": {
                "count": len(file_data),
                "data": file_data
            },
            "image_data": {
                "count": len(image_data),
                "data": image_data
            }
        }
        return data
    
class FormatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)
    unseen_message_count = serializers.SerializerMethodField(source='get_unseen_message_count', read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date',
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'unseen_message_count', 'room_id']

    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj).order_by('-id').first()
        sz = GetMessageSerializer(message)
        return sz.data

    def get_unseen_message_count(self, obj):
        count = Message.objects.filter(room_id=obj, is_seen__isnull=True).count()
        return count
    
   


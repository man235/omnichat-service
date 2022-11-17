from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message, FanPage, Room, ServiceSurvey, UserApp, Label, LogMessage,AssignReminder
from django.db.models import Q
from sop_chat_service.utils.remove_accent import remove_accent
from .reminder_serializers import GetAssignReminderSerializer
from sop_chat_service.utils.request_headers import get_user_from_header


class LogMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogMessage
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'mid', 'type', 'url', 'name', 'size']
class ServiceSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSurvey
        fields = ['id', 'mid', 'name', 'value']
class GetMessageSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)
    log_message = serializers.SerializerMethodField(source='get_log_message', read_only=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender', 'created_at', 'uuid', 'log_message']

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id)
        sz = AttachmentSerializer(attachments, many=True)
        return sz.data

    def get_log_message(self,obj):
        _msg_log = LogMessage.objects.filter(mid=obj.id).first()
        sz = LogMessageSerializer(_msg_log)
        return sz.data


class FanpageInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanPage
        fields = ['name', 'avatar_url']

class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)
    unseen_message_count = serializers.SerializerMethodField(source='get_unseen_message_count', read_only=True)
    fanpage = serializers.SerializerMethodField(source='get_fanpage', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date', 'status',
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'room_id',"unseen_message_count", "fanpage"]
        
    def get_unseen_message_count(self, obj):
        count = Message.objects.filter(room_id=obj, is_seen__isnull=True).count()
        return count
    
    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj, is_sender=False).order_by('-id').first()
        sz = GetMessageSerializer(message)
        return sz.data
    
    def get_fanpage(self, obj):
        if not obj.page_id:
            return None
        fanpage_info = FanPage.objects.filter(id=obj.page_id.id).first()
        sz_fanpage_info = FanpageInfoSerializer(fanpage_info)
        return sz_fanpage_info.data

class RoomIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id"]




class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["label_id"]



class RoomMessageSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)
    unseen_message_count = serializers.SerializerMethodField(source='get_unseen_message_count', read_only=True)
    user_info = serializers.SerializerMethodField(source='get_user_info', read_only=True)
    fanpage = serializers.SerializerMethodField(source='get_fanpage', read_only=True)
    label = serializers.SerializerMethodField(source='get_label', read_only=True)
    assign_reminder = serializers.SerializerMethodField(source='get_assign_reminder', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date', 'status','assign_reminder',
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'unseen_message_count', 'room_id', 'user_info', 'fanpage', 'label']
    
    def get_assign_reminder(self,obj):
        assign_reminder = AssignReminder.objects.filter(room_id = obj, user_id= obj.user_id).order_by('-created_at').first()
        if not assign_reminder :
            return None
        sz = GetAssignReminderSerializer(assign_reminder,many=False)
        result = sz.data if sz.data else None
        return result
    
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
        if obj.type == "livechat":
            return {
                "avatar":None,
                "name": obj.name,
                "external_id":obj.external_id,
                "email":None,
                "gender":None,
                "id":None,
                "phone":None
            }
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
class SearchRoomSerializer(serializers.Serializer):
    search = serializers.CharField(required=True)
    is_filter =serializers.BooleanField(required=True)
  
class SearchMessageSerializer(serializers.Serializer):
    room_id= serializers.CharField(required=True)
    search = serializers.CharField(required=True)
    def validate(self, request, attrs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)),room_id=attrs.get("room_id")).first()
        if not room:
            raise serializers.ValidationError({"room": "Room Invalid"})
        
        return room,remove_accent(attrs.get('search'))
class RoomInfoSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=False)
    def validate(self, request, attrs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)),room_id=attrs.get("room_id")).first()
        if not room:
            raise serializers.ValidationError({"room": "Room Invalid"})
        return room
    

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
class InfoSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)
    unseen_message_count = serializers.SerializerMethodField(source='get_unseen_message_count', read_only=True)
    user_info = serializers.SerializerMethodField(source='get_user_info', read_only=True)
    fanpage = serializers.SerializerMethodField(source='get_fanpage', read_only=True)
    label = serializers.SerializerMethodField(source='get_label', read_only=True)
    assign_reminder = serializers.SerializerMethodField(source='get_assign_reminder', read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date', 'status',"assign_reminder",
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'unseen_message_count', 'room_id', 'user_info', 'fanpage', 'label']

    def get_assign_reminder(self,obj):
        assign_reminder = AssignReminder.objects.filter(room_id = obj, user_id= obj.user_id).order_by('-created_at').first()
        # if not assign_reminder :
        #     return None
        sz = GetAssignReminderSerializer(assign_reminder,many=False)
        result = sz.data if sz.data else None
        return result
    
    def get_last_message(self, obj):
        if obj.type.lower() == "facebook":
            message = Message.objects.filter(room_id=obj, is_sender=False).order_by('-id').first()
            sz = GetMessageSerializer(message)
            return sz.data
        else:
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
        label = Label.objects.filter(room_id=obj)
        sz = LabelSerializer(label, many=True)
        return sz.data
    
    
class CompleteRoomSerializer(serializers.Serializer):
    is_complete = serializers.BooleanField(required=True)
    

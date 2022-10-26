
from rest_framework import serializers
from sop_chat_service.app_connect.serializers.room_serializers import GetMessageSerializer
from ...app_connect.models import Attachment, Message, Room, UserApp
from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo, UserLiveChat


class LiveChatSerializer(serializers.ModelSerializer):
    register_info = serializers.SerializerMethodField(source='get_register_info', read_only=True)
    class Meta:
        model = LiveChat
        fields = '__all__'

    def get_register_info(self, obj):
        register_info = LiveChatRegisterInfo.objects.filter(live_chat_id=obj.id)
        sz = RegisterInfoSerializer(data=register_info, many=True)
        sz.is_valid()
        return sz.data

class CreateLiveChatSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True),
    name =serializers.CharField(max_length=50,required=True)
    name_agent =serializers.CharField(max_length=50,required=True)
    color = serializers.CharField(max_length=10,required=True)
    icon_content= serializers.CharField(max_length=50,required=False)
    start_btn = serializers.CharField(max_length=50,required=False)
    introduce_message = serializers.CharField(max_length=300,required=False)
    start_message =serializers.CharField(max_length=300,required=False)
    offline_message =serializers.CharField(max_length=300,required=False)
    class Meta:
        model = LiveChat
        fields = '__all__'

class UpdateAvatarLiveChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveChat
        fields = ["avatar"]


class RegisterInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveChatRegisterInfo
        fields = '__all__'


class MessageLiveChatSend(serializers.Serializer):
    message_text = serializers.CharField(required=False)
    room_id = serializers.CharField(required=True)
    mid = serializers.CharField(required=False)
    is_text = serializers.BooleanField(required=True)
    recipient_id = serializers.CharField(required=False)

    class Meta:
        fields = ['file', 'message_text', 'room_id', 'mid', 'message_type']
    def validate(self, attrs):
    
        file= self.context['request'].FILES.getlist('file')
        if attrs.get("room_id"):
            room= Room.objects.filter(room_id=attrs.get("room_id")).first()
            if not room or room.status == "expired" or room.status =="completed":
                raise serializers.ValidationError({"room_id": "Room is Invalid"})
        if str(attrs.get("is_text")).lower() == "true":
            if not attrs.get("message_text"):
                raise serializers.ValidationError({"message_text": "message is required"})
        if str(attrs.get("is_text")).lower() == "false":
            if not file:
                raise serializers.ValidationError({"file": "file is required"})
        if attrs.get("mid"):
            message = Message.objects.get(id = attrs.get('mid'))
            if not message:
                raise serializers.ValidationError({"mid": "Message is Invalid"})

        return attrs

class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(source='get_url', read_only=True)

    class Meta:
        model = Attachment
        fields = ['mid', 'type', 'url']

    def get_url(self, obj):
        return obj.file.url


class GetMessageLiveChatSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender']

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id)
        sz = AttachmentSerializer(attachments, many=True)
        return sz.data


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'approved_date', 'type', 'completed_date', 'last_message']

    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj).order_by('-id').first()
        sz = GetMessageLiveChatSerializer(message)
        return sz.data
class CreateUserLiveChatSerializers(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    value = serializers.CharField(required=False)
    class Meta:
        model = UserLiveChat
        fields =[ 'title','value']
class RoomLiveChatSerializer(serializers.ModelSerializer):
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
    
class CompletedRoomSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)

    class Meta:
        fields = [ 'room_id']
    def validate(self, attrs):
        if attrs.get("room_id"):
            room= Room.objects.filter(id=attrs.get("room_id")).first()
            if not room or room.status == "expired":
                raise serializers.ValidationError({"room_id": "Room is Invalid"})
        return attrs
class StartSerializer(serializers.Serializer):
    live_chat_id = serializers.IntegerField(required= True)
    def validate(self, attrs):
        if not attrs.get("live_chat_id"):
            raise serializers.ValidationError({"live_chat_id": "live_chat_id is required"})
        if attrs.get("live_chat_id"):
            live_chat= LiveChat.objects.filter(id=attrs.get("live_chat_id")).first()
            if not live_chat:
                raise serializers.ValidationError({"live_chat_id": "Live Chat Is Invalid"})
        return attrs
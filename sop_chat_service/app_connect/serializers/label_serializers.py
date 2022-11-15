from rest_framework import serializers
from sop_chat_service.app_connect.models import Label

from sop_chat_service.app_connect.models import Room
from sop_chat_service.utils.request_headers import get_user_from_header


class CreateLabelSerializer(serializers.ModelSerializer):
    room_id = serializers.CharField(required=True)
    label_id=  serializers.ListField(child=serializers.CharField(),required=True)

    class Meta:
        model = Label
        fields = [ "label_id", "room_id"]

class UpdateLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "label_id", "room_id"]
class GetLabelSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    def validate(self, request, attrs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter(room_id=attrs.get("room_id"), user_id=user_header).first()
        return room,user_header

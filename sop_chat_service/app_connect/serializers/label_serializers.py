from rest_framework import serializers
from sop_chat_service.app_connect.models import Label


class CreateLabelSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    color = serializers.CharField(required=True)

    class Meta:
        model = Label
        fields = ["name", "color", "room_id"]

class UpdateLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "name", "color", "room_id"]

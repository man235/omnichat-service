from rest_framework import serializers
from sop_chat_service.app_connect.models import Room, FanPage


class MessageFacebookSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    message_text = serializers.CharField(required=False)
    # attachment_type = serializers.CharField(required=False)
    is_text = serializers.BooleanField(required=True)

    def validate(self, request, attrs):
        if str(attrs.get("is_text")).lower() == "true":
            if not attrs.get("message_text"):
                raise serializers.ValidationError({"message_text": "message_text not null"})
            room = Room.objects.get(id=attrs.get("room_id"))
            data = {
                "messaging_type": "MESSAGE_TAG",
                "recipient": {
                    "id": attrs.get("recipient_id")
                },
                "tag": "NON_PROMOTIONAL_SUBSCRIPTION",
                "message": {
                    "text": attrs.get("message_text")
                }
            }
            return room, data, False

        if str(attrs.get("is_text")).lower() == "false":
            # if not attrs.get("attachment_type"):
            #     raise serializers.ValidationError({"attachment_type": "attachment_type not null"})
            room = Room.objects.get(id=attrs.get("room_id"))
            recipient = str({"id": attrs.get("recipient_id")})
            file = request.FILES['file']
            content_type = file.content_type.split('/')[0]
            types = ''
            if content_type == "application":
                types = 'file'
            else:
                types = content_type
            files = [
                ('filedata', (file.name, file, file.content_type))
            ]
            payload = {
                'recipient': recipient,
                'message': "{" + '"attachment"' + " : "+"{" + '"type"' + ":"+f'"{types}"'+"," + '"payload"'+":" + "{"+'"is_reusable"'+":"+"true}}}"
            }
            data = {
                "payload": payload,
                "files": files
            }
            return room, data, True

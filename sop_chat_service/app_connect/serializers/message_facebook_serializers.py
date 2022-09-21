from rest_framework import serializers
from sop_chat_service.app_connect.models import Room, FanPage


class MessageFacebookSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    message_text = serializers.CharField(required=False)
    # attachment_type = serializers.CharField(required=False)
    is_text = serializers.BooleanField(required=True)

    def validate(self, request, attrs):
        room = Room.objects.get(room_id=attrs.get("room_id"))
        recipient_id = attrs.get("recipient_id")
        if str(attrs.get("is_text")).lower() == "true":
            if not attrs.get("message_text"):
                raise serializers.ValidationError({"message_text": "message_text not null"})
            data = {
                "messaging_type": "MESSAGE_TAG",
                "recipient": {
                    "id": recipient_id
                },
                "tag": "NON_PROMOTIONAL_SUBSCRIPTION",
                "message": {
                    "text": attrs.get("message_text")
                }
            }
            return room, data, False

        if str(attrs.get("is_text")).lower() == "false":
            # room = Room.objects.get(room_id=attrs.get("room_id"))
            recipient = str({"id": recipient_id})
            files = request.FILES.getlist('file')
            files_data = []
            for file in files:
                content_type = file.content_type.split('/')[0]
                types = ''
                if content_type == "application":
                    types = 'file'
                else:
                    types = content_type
                file_data = [('filedata', (file.name, file, file.content_type))]
                files_data.append(file_data)
            payload = {
                'recipient': recipient,
                'message': "{" + '"attachment"' + " : "+"{" + '"type"' + ":"+f'"{types}"'+"," + '"payload"'+":" + "{"+'"is_reusable"'+":"+"true}}}"
            }
            data = {
                "payload": payload,
                "files": files_data
            }
            return room, data, True

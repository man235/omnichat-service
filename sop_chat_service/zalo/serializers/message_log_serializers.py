from rest_framework import serializers

from sop_chat_service.app_connect.models import LogMessage


class MessageLogSerializer(serializers.modelSerializer):
    
    class Meta:
        model = LogMessage
        fields = [
            'from_user',
            'to_user',
            'mid__text',
        ]
    
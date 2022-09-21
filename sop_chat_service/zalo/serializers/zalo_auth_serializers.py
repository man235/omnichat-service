
from rest_framework import serializers

from sop_chat_service.app_connect.models import FanPage

class ZaloAuthenticationSerializer(serializers.Serializer):
    authorization_code = serializers.CharField(required=True)
    code_verifier = serializers.CharField(required=False)


class ZaloConnectPageSerializer(serializers.Serializer):
    is_subscribed = serializers.BooleanField(required=False)
    oa_id = serializers.CharField(required=True)

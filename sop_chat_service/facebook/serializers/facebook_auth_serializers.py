
from rest_framework import serializers
from sop_chat_service.app_connect.models import FanPage


class FacebookAuthenticationSerializer(serializers.Serializer):
    redirect_url = serializers.CharField(required=True)
    code = serializers.CharField(required=True)


class FacebookConnectPageSerializer(serializers.Serializer):
    is_subscribe = serializers.BooleanField(required=True)
    page_id = serializers.CharField(required=True)

class DeleteFanPageSerializer(serializers.Serializer):
    id =  serializers.ListField(child=serializers.IntegerField(min_value=0))
    class Meta:
       fields = ['id']
    def validate(self, attrs):
        for item in attrs.get("id"):
            page = FanPage.objects.filter(id=item).first()
            if not page:
                raise serializers.ValidationError({"id": "FanPage Invalid"})
        return attrs
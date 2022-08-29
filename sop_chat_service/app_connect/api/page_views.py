
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer
from sop_chat_service.app_connect.models import FanPage


from sop_chat_service.facebook.utils import custom_response


class FanPageViewSet(viewsets.ModelViewSet):
    serializer_class = FanPageSerializer
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        qs = FanPage.objects.filter(is_active=True).exclude(last_subscribe=None)
        sz = FanPageSerializer(qs, many=True)
        return custom_response(200, "Get List Page Successfully", sz.data)

from django.conf import settings
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from core import constants
from sop_chat_service.app_connect.models import FanPage, Room
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.zalo.utils.api_suport import get_oa_queryset_by_user_id
from .page_serializers import FanPageSerialier, GetFanPageSerialier
from django.db.models import Q

class PageViewSet(viewsets.ModelViewSet):
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = FanPageSerialier
    
    @action(detail=False, methods=["POST"], url_path="page-list")
    def get_page(self,request,*args, **kwargs):
        user_header= get_user_from_header(request.headers)
        serializer =GetFanPageSerialier(data=request.data)
        serializer.is_valid(raise_exception=True)

        page_getter_type = serializer.data.get('type')
        
        if page_getter_type == constants.ZALO:
            page_queryset = get_oa_queryset_by_user_id(user_header)
        elif page_getter_type in (constants.LIVECHAT, constants.FACEBOOK):
            page_queryset = FanPage.objects.filter(
                type=page_getter_type,
                user_id=user_header,
                is_deleted=False,
            )
        else:
            return custom_response(
                400,
                'Invalid type'
            )

        response_data = {
            'count': page_queryset.count(),
            'page_list': FanPageSerialier(page_queryset, many=True).data
        }
        
        return custom_response(
            200, 
            "Get List Page Successfully",
            response_data
        )

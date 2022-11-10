from django.conf import settings
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from sop_chat_service.app_connect.models import FanPage,Room
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from .page_serializers import FanPageSerialier,GetFanPageSerialier
from django.db.models import Q

class PageViewSet(viewsets.ModelViewSet):
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = FanPageSerialier
    
    
    
    @action(detail=False, methods=["POST"], url_path="list-page")
    def get_page(self,request,*args, **kwargs):
        user_header= get_user_from_header(request.headers)
        sz =GetFanPageSerialier(data=request.data)
        sz.is_valid(raise_exception=True)
        qs=[]
        if sz.data['type'] == 'all':
            qs = FanPage.objects.filter((Q(user_id=user_header) | Q(group_user__contains= [user_header])))
        else:
            qs = FanPage.objects.filter((Q(user_id=user_header) | Q(group_user__contains= [user_header])), type=sz.data['type'])
        zalo_page = qs.filter(type ='zalo')
        for item in zalo_page:
            room = Room.objects.filter(user_id =user_header , page_id=item)
            if not room:
                qs.exclude(id = item.id)
        count = qs.count()
        
        page_sz = FanPageSerialier(qs,many=True)
        data = {
            "count":count,
            "list_page":page_sz.data
        }
        return custom_response(200,"Get List Page Successfully",data)
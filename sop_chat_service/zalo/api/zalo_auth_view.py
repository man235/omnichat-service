import requests
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework import permissions, status

from config.settings.local import ZALO_APP_SECRET_KEY, ZALO_OA_OPEN_API
from sop_chat_service.app_connect.models import FanPage
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.zalo.serializers.zalo_auth_serializers import ZaloAuthenticationSerializer, ZaloConnectPageSerializer
from sop_chat_service.zalo.utils import zalo_oa_auth


class ZaloViewSet(viewsets.ModelViewSet):
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = FanPageSerializer
        
    @action(detail=False, methods=['post'], url_path='subscribe')
    def connect_oa(self, request, *args, **kwargs) -> Response:
        """
        API connect/reconnect to Zalo OA
        """
        oa_connection_sz = ZaloConnectPageSerializer(data=request.data)
        if oa_connection_sz.is_valid(raise_exception=True):
            oa_auth_sz = ZaloAuthenticationSerializer(data=request.data)
            oa_auth_sz.is_valid(raise_exception=True)
            oa_token_json = zalo_oa_auth.get_oa_token(
                oa_auth_sz.validated_data.get('oa_id'),
                oa_auth_sz.validated_data.get('authorization_code'),
                oa_auth_sz.validated_data.get('code_verifier')
            )

            if not oa_token_json:
                return custom_response(status.HTTP_400_BAD_REQUEST)
            elif oa_token_json.get('message') != 'Success':
                return custom_response(status.HTTP_400_BAD_REQUEST, 
                                       oa_token_json.get('error'))

            access_token = oa_token_json.get('data').get('access_token')
            refresh_token = oa_token_json.get('data').get('refresh_token')
            oa_info_reponse = zalo_oa_auth.get_oa_info(access_token)
            oa_info_json = oa_info_reponse.json()
        
            if oa_info_reponse.status_code == 200:
                if oa_info_json.get('message') == 'Success':
                    oa_data: dict = oa_info_json.get('data')
                    try:                  
                        oa_data_bundle = {
                            'page_id': oa_data.get('oa_id'),
                            'name': oa_data.get('name'),
                            'access_token_page': access_token,
                            'refresh_token_page': refresh_token,
                            'avatar_url': oa_data.get('avatar'),
                            'is_active': True,
                            'created_by': request.user.id,
                        }
                        oa_sz = self.get_serializer(data=oa_data_bundle)
                        if oa_sz.is_valid():
                            # is_subscribed = oa_connection_sz.validated_data.get('is_subscribed')             
                            oa_queryset = FanPage.objects.filter(page_id=
                                                                 oa_data.get('oa_id')
                                                                ).first()                                           
                            if not oa_queryset:
                                oa_model = oa_sz.create(oa_data_bundle)
                            else:
                                oa_model = oa_sz.update(oa_queryset, oa_data_bundle)
                            return custom_response(status.HTTP_200_OK, 'Success', self.get_serializer(oa_model).data)
                        else:
                            return custom_response(status.HTTP_500_INTERNAL_SERVER_ERROR)
                    except Exception as e:
                        return custom_response(status.HTTP_401_UNAUTHORIZED, e)
            else:
                return custom_response(status.HTTP_400_BAD_REQUEST)
        else:
            return custom_response(status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='delete')
    def delete_oa(self, request, *args, **kwargs) -> Response:
        """
        API delete Zalo OA
        """
        sz = ZaloConnectPageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        FanPage.objects.filter(page_id=sz.validated_data.get('oa_id')).delete()
        
        return custom_response(200, 'Delete OA successfully', [])
    
    @action(detail=False, methods=['post'], url_path='unsubscribe')
    def unsubscribe_oa(self, request, *args, **kwargs) -> Response:
        """
        API delete Zalo OA
        """
        sz = ZaloConnectPageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        FanPage.objects.filter(page_id=sz.validated_data.get('oa_id')).update(is_active=False)

        return custom_response(200, 'Unsubscribe to Zalo OA successfully', [])
        
    @action(detail=False, methods=['post'], url_path='list')
    def get_oa_list(self, request, *args, **kwargs) -> Response:
        """
        API get Zalo OA list
        """
        oa_queryset = FanPage.objects.all()
        oa_serializer = self.get_serializer(oa_queryset, many=True)
        
        for item in oa_serializer.data:
            data = dict(item)
      
            if data.get('is_active'):
                oa = FanPage.objects.get(page_id=data.get('page_id'))   
                time_remaining = oa.last_subscribe  
                expired_access, expired_refresh = zalo_oa_auth.check_valid_token(time_remaining)
            
                if expired_refresh:
                    FanPage.objects.filter(page_id=data.get('page_id')).update(is_active=False)
                elif expired_access:
                    token_json = zalo_oa_auth.get_oa_token(refresh_token=
                                                           data.get('refresh_token_page'))
                    
                    if token_json.get('message') != 'Success':
                        new_access_token = token_json.get('data').get('access_token')
                        new_refresh_token = token_json.get('data').get('refresh_token')
                        FanPage.objects.filter(page_id=data.get('page_id')).update(access_token_page=new_access_token,
                                                                                    refresh_token_page=new_refresh_token)
                    else:
                        FanPage.objects.filter(page_id=data.get('page_id')).update(is_active=False)
         
        return custom_response(message='Success', data=oa_serializer.data)
        
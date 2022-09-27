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
    serializer_class = ZaloAuthenticationSerializer
        
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
                return custom_response(400, 'Failure')
            elif oa_token_json.get('message') != 'Success':
                return custom_response(400, oa_token_json.get('error'))

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
                        oa_sz = FanPageSerializer(data=oa_data_bundle)
                        if oa_sz.is_valid(raise_exception=True):
                            # is_subscribed = oa_connection_sz.validated_data.get('is_subscribed')             
                            oa_queryset = FanPage.objects.filter(page_id=
                                                                 oa_data.get('oa_id')
                                                                ).first()                                           
                            if not oa_queryset:
                                oa_model = oa_sz.create(oa_data_bundle)
                            else:
                                oa_model = oa_sz.update(oa_queryset, oa_data_bundle)
                            return custom_response(200, 'Success', FanPageSerializer(oa_model).data)
                        else:
                            return custom_response(400, 'Failure')
                    except Exception as e:
                        return custom_response(500, str(e))
            else:
                return custom_response(401, 'Failed to authorize')
        else:
            return custom_response(400, 'Bad request')
    
    @action(detail=False, methods=['post'], url_path='delete')
    def delete_oa(self, request, *args, **kwargs) -> Response:
        """
        API delete Zalo OA
        """
        sz = ZaloConnectPageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        qs = FanPage.objects.filter(page_id=sz.validated_data.get('oa_id'))
        if qs:
            qs.delete()
            return custom_response(200, 'Deleted Zalo OA successfully')
        return custom_response(400, 'Failed to delete Zalo OA', [])

    
    @action(detail=False, methods=['post'], url_path='unsubscribe')
    def unsubscribe_oa(self, request, *args, **kwargs) -> Response:
        """
        API delete Zalo OA
        """
        sz = ZaloConnectPageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        qs = FanPage.objects.filter(page_id=sz.validated_data.get('oa_id'))
        if qs:
            qs.update(is_active=False)
            return custom_response(200, 'Unsubscribe Zalo OA successfully')
        return custom_response(400, 'Failed to unsubscribe Zalo OA', [])
        
    @action(detail=False, methods=['post'], url_path='getoa')
    def get_oa_list(self, request, *args, **kwargs) -> Response:
        """
        API get Zalo OA list
        """
        oa_queryset = FanPage.objects.all()
        oa_serializer = FanPageSerializer(oa_queryset, many=True)
        
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

        # Update FanPage Serializers
        oa_serializer = FanPageSerializer(FanPage.objects.all(), many=True)
        return custom_response(message='Success', data=oa_serializer.data)
    
    @action(detail=False, methods=['post'], url_path='oa-list')
    def get_oa_list_v2(self, request, *args, **kwargs) -> Response:
        """
        API get Zalo OA list
        """
        oa_queryset = FanPage.objects.all()
        oa_serializer = FanPageSerializer(oa_queryset, many=True)
        
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

        # Update FanPage Serializers
        oa_serializer = FanPageSerializer(FanPage.objects.all(), many=True)
        return custom_response(message='Success', data=oa_serializer.data)
    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh_token(self, request, *args, **kwargs) -> Response:
        """
        API refresh tokens
        """
        
        serializer = ZaloConnectPageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        oa_id = serializer.data.get('oa_id')
        queryset = FanPage.objects.filter(page_id=oa_id)
        if queryset:
            refresh_token_page = FanPage.objects.get(page_id=oa_id).refresh_token_page
            if refresh_token_page:
                oa_token = zalo_oa_auth.get_oa_token(oa_id=oa_id, refresh_token=refresh_token_page)
                if not oa_token:
                    return custom_response(400, 'Failure')
                if oa_token.get('message') == 'Success':
                    access_token = oa_token.get('data').get('access_token')
                    refresh_token = oa_token.get('data').get('refresh_token')
                    
                    queryset.update(access_token_page=access_token,
                                    refresh_token_page=refresh_token)
                    
                    return custom_response(200, 'Success')
                else:
                    return custom_response(400, oa_token.get('error'))
            return custom_response(401, 'Failure')
        else:
            return custom_response(400, 'Zalo OA not found')

                
                
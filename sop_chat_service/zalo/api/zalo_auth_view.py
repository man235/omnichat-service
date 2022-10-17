import json
from time import time
from django.utils import timezone
import requests
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework import permissions, status
from config.settings.local import ZALO_APP_SECRET_KEY, ZALO_OA_OPEN_API
from sop_chat_service.app_connect.models import FanPage
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.zalo.serializers.zalo_auth_serializers import ZaloAuthenticationSerializer, ZaloConnectPageSerializer
from sop_chat_service.zalo.utils.api_suport import zalo_oa_auth
import logging

logger = logging.getLogger(__name__)


class ZaloViewSet(viewsets.ModelViewSet):
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ZaloAuthenticationSerializer
        
    @action(detail=False, methods=['post'], url_path='subscribe')
    def connect_oa(self, request, *args, **kwargs) -> Response:
        """
        API connect/reconnect to Zalo OA
        """
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)
        oa_connection_sz = ZaloConnectPageSerializer(data=request.data)
        if oa_connection_sz.is_valid(raise_exception=True):
            oa_auth_sz = ZaloAuthenticationSerializer(data=request.data)
            oa_auth_sz.is_valid(raise_exception=True)
            oa_token = zalo_oa_auth.get_oa_token(
                oa_auth_sz.data.get('oa_id'),
                oa_auth_sz.data.get('authorization_code'),
                oa_auth_sz.data.get('code_verifier')
            )

            if not oa_token:
                return custom_response(401, 'Failed to authorize Zalo OA')
            elif oa_token.get('message') != 'Success':
                return custom_response(400, oa_token.get('error'))

            access_token = oa_token.get('data').get('access_token')
            refresh_token = oa_token.get('data').get('refresh_token')

            oa_info = zalo_oa_auth.get_oa_info(access_token)
            if not oa_info:
                return custom_response(403, 'Failed to get Zalo OA infomation')
            elif oa_info.get('message') != 'Success':
                return custom_response(400, oa_info.get('eror'))
            else:
                oa_data = oa_info.get('data')
                try:                  
                    oa_data_bundle = {
                        'page_id': oa_data.get('page_id'),
                        'type': 'zalo',
                        'name': oa_data.get('name'),
                        'user_id': user_header,
                        'access_token_page': access_token,
                        'refresh_token_page': refresh_token,
                        'avatar_url': oa_data.get('avatar_url'),
                        'is_active': True,
                        'created_by': request.user.id,
                        'last_subscribe': str(timezone.now())
                    }
                    oa_sz = FanPageSerializer(data=oa_data_bundle)

                    if oa_sz.is_valid(raise_exception=True):
                        # is_subscribed = oa_connection_sz.validated_data.get('is_subscribed')             
                        oa_queryset = FanPage.objects.filter(
                            page_id=oa_data.get('page_id')
                        ).first()                                           
                        if not oa_queryset:
                            oa_model = oa_sz.create(oa_data_bundle)
                        else:
                            oa_model = oa_sz.update(oa_queryset, oa_data_bundle)
                        
                        return custom_response(
                            200,
                            'Connect to Zalo OA successfully',
                            FanPageSerializer(oa_model).data
                        )
                    else:
                        return custom_response(500, 'Failed to serialize data')
                except Exception as e:
                    return custom_response(500, str(e))
        else:
            return custom_response(400, 'Bad request')
    
    @action(detail=False, methods=['post'], url_path='delete')
    def delete_oa(self, request, *args, **kwargs) -> Response:
        """
        API delete Zalo OA
        """
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)
        sz = ZaloConnectPageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        qs = FanPage.objects.filter(
            page_id=sz.data.get('oa_id'),
            user_id=user_header,
        ).first()
        if qs:
            qs.delete()
            return custom_response(200, 'Delete Zalo OA successfully')
        return custom_response(
            400,
            'Failed to delete. May be you are not the first admin connect to this OA',
            []
        )
    
    @action(detail=False, methods=['post'], url_path='unsubscribe')
    def unsubscribe_oa(self, request, *args, **kwargs) -> Response:
        """
        API delete Zalo OA
        """
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)
        sz = ZaloConnectPageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        qs = FanPage.objects.filter(
            page_id=sz.data.get('oa_id'),
            user_id=user_header,
        ).first()
        if qs:
            qs.is_active = False
            qs.last_subscribe = timezone.now()
            qs.save()
            return custom_response(200, 'Disconnect Zalo OA successfully')
        return custom_response(
            400,
            'Failed to disconnect. May be you are not the first admin connect to this OA',
            []
        )      
    
    @action(detail=False, methods=['post'], url_path='oa-list')
    def get_oa_list_v2(self, request, *args, **kwargs) -> Response:
        """
        API get Zalo OA list
        """
        oa_queryset = FanPage.objects.filter(type='zalo')
        oa_serializer = FanPageSerializer(oa_queryset, many=True)

        for item in oa_serializer.data:
            data = dict(item)
            
            if not data.get('is_active'):
                continue
            
            oa_id = data.get('page_id')
            oa_model = FanPage.objects.filter(page_id=oa_id).first()
            access_token = oa_model.access_token_page
            oa_info = zalo_oa_auth.get_oa_info(access_token)

            if not oa_info or oa_info.get('message') != 'Success':
                oa_model.is_active = False
                oa_model.last_subscribe = timezone.now()
                oa_model.save()
            else:
                oa_data = oa_info.get('data')
                oa_model.name = oa_data.get('name')
                oa_model.avatar_url = oa_data.get('avatar_url')
                oa_model.created_by = request.user.id
                # oa_model.last_subscribe = timezone.now()
                oa_model.save()
                
        # Update FanPage Serializers
        oa_updated_serializer = FanPageSerializer(
            FanPage.objects.filter(type='zalo'),
            many=True
        )
        return custom_response(
            message='Request successfully', 
            data=oa_updated_serializer.data
        )
    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh_token(self, request, *args, **kwargs) -> Response:
        """
        API refresh tokens
        """
        serializer = ZaloConnectPageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        oa_id = serializer.data.get('oa_id')
        queryset = FanPage.objects.filter(page_id=oa_id).first()
        
        if queryset:
            refresh_token_page = queryset.refresh_token_page

            if refresh_token_page:
                oa_token = zalo_oa_auth.get_oa_token(oa_id=oa_id, refresh_token=refresh_token_page)
                
                if not oa_token or oa_token.get('message') == 'Failure':
                    queryset.is_active = False
                    queryset.last_subscribe = timezone.now()
                    queryset.save()
                    return custom_response(401, 'Failed to authorize Zalo OA')

                if oa_token.get('message') == 'Success':
                    access_token = oa_token.get('data').get('access_token')
                    refresh_token = oa_token.get('data').get('refresh_token')
                    
                    queryset.access_token_page = access_token
                    queryset.refresh_token_page = refresh_token
                    queryset.is_active = True
                    queryset.last_subscribe = timezone.now()
                    queryset.save()
                    
                    return custom_response(200, 'Refresh Zalo access successfully')
                else:
                    return custom_response(400, oa_token.get('error'))
            return custom_response(400, 'Can not refresh Zalo OA')
        else:
            return custom_response(400, 'Zalo OA not found')

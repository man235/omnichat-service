from django.utils import timezone
from jinja2 import is_undefined
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework import permissions, status
from sop_chat_service.app_connect.models import FanPage, Room
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer, SettingChatZaloSerializer
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.zalo.serializers.zalo_auth_serializers import ZaloAuthenticationSerializer, ZaloConnectPageSerializer
from sop_chat_service.zalo.utils.api_suport import zalo_oa_auth
from core import constants
from django.db.models import Q
from sop_chat_service.zalo.utils.api_suport.zalo_oa_filter import get_oa_queryset_by_user_id
from sop_chat_service.zalo.utils.api_suport.zalo_oa_filter import get_oa_queryset_by_user_id
import logging

logger = logging.getLogger(__name__)


class ZaloViewSet(viewsets.ModelViewSet):
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ZaloAuthenticationSerializer
        
    @action(detail=False, methods=['post'], url_path='subscribe')
    def connect_oa(self, request, *args, **kwargs) -> Response:
        """
        API connect to Zalo OA
        """
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)
        oa_connection_sz = ZaloConnectPageSerializer(data=request.data)

        if oa_connection_sz.is_valid(raise_exception=True):
            queryset = FanPage.objects.filter(
                page_id=oa_connection_sz.data.get('oa_id'),
                type='zalo',
            ).first()
            
            # Verify the first Zalo OA owner
            if queryset and not queryset.is_deleted:
                if not queryset.user_id == user_header:
                    return custom_response(
                        400,
                        'Zalo OA is connected. May be you are not the first admin connect to this OA',
                    )
                
            oa_auth_sz = ZaloAuthenticationSerializer(data=request.data)
            oa_auth_sz.is_valid(raise_exception=True)
            oa_token = zalo_oa_auth.get_oa_token(
                oa_auth_sz.data.get('authorization_code'),
                oa_auth_sz.data.get('code_verifier')
            )

            if not oa_token:
                return custom_response(400, 'Failed to authorize Zalo OA')
            elif oa_token.get('message') != 'Success':
                return custom_response(400, oa_token.get('error'))

            access_token = oa_token.get('data').get('access_token')
            refresh_token = oa_token.get('data').get('refresh_token')

            oa_info = zalo_oa_auth.get_oa_info(access_token)
            if not oa_info:
                return custom_response(400, 'Failed to get Zalo OA infomation')
            elif oa_info.get('message') != 'Success':
                return custom_response(400, oa_info.get('error'))
            else:
                oa_data = oa_info.get('data')
                
                # 2 oa id must be matched
                if oa_connection_sz.data.get('oa_id') != oa_data.get('page_id'):
                    return custom_response(400, 'The connecting Zalo OA id doesn\'t match with the required OA id')
                
                try:                  
                    oa_data_bundle = {
                        'page_id': oa_data.get('page_id'),
                        'type': 'zalo',
                        'name': oa_data.get('name'),
                        'user_id': user_header,
                        'access_token_page': access_token if oa_connection_sz.data.get('is_subscribe') else 'Invalid',
                        'refresh_token_page': refresh_token,
                        'avatar_url': oa_data.get('avatar_url'),
                        'is_active': True if oa_connection_sz.data.get('is_subscribe') else False,
                        'is_deleted': False,
                        'created_by': user_header,
                        'last_subscribe': str(timezone.now())
                    }
                    oa_sz = FanPageSerializer(data=oa_data_bundle)

                    if oa_sz.is_valid(raise_exception=True):                                        
                        if not FanPage.objects.filter(
                            page_id=oa_data.get('page_id'),
                            type='zalo'
                        ):
                            oa_model = oa_sz.create(oa_data_bundle)
                        else:
                            oa_model = oa_sz.update(queryset, oa_data_bundle)
                            
                            # update user id or admin id fields in room model
                            room_qs = Room.objects.filter(
                                page_id=oa_model,
                                type=constants.ZALO
                            )
                            updating_room_data = {}
                            # updating_room_data = {
                            #     'admin_room_id': oa_model.user_id
                            # }
                            if oa_model.setting_chat == constants.SETTING_CHAT_ONLY_ME:
                                updating_room_data['user_id'] = oa_model.user_id
                            elif oa_model.setting_chat != constants.SETTING_CHAT_ONLY_ME:
                                updating_room_data['admin_room_id'] = user_header
                            room_qs.update(
                                **updating_room_data
                            )

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
            return custom_response(400, 'Can not connect to Zalo OA')
    
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
            is_deleted=False
        ).first()
        
        if not qs:
            return custom_response(
                400,
                'Failed to delete. Zalo OA not found',
            )
        
        if qs.user_id == user_header:
            qs.is_deleted = True
            qs.is_active = False
            qs.access_token_page = 'Invalid'
            qs.save()
            return custom_response(200, 'Delete OA successfully')    
        else:
            return custom_response(
                400,
                'Failed to delete. May be you are not the first admin connect to this OA',
            )
            
    @action(detail=False, methods=['post'], url_path='unsubscribe')
    def unsubscribe_oa(self, request, *args, **kwargs) -> Response:
        """
        API disconnect Zalo OA
        """
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)
        sz = ZaloConnectPageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        qs = FanPage.objects.filter(
            page_id=sz.data.get('oa_id'),
            is_deleted=False
        ).first()
        
        if not qs:
            return custom_response(
                400,
                'Failed to disconnect. Zalo OA not found',
            )
        
        if qs.user_id == user_header:
            qs.is_active = False
            qs.access_token_page = 'Invalid'
            qs.last_subscribe = timezone.now()
            qs.save()
            
            return custom_response(200, 'Disconnect OA successfully')    
        else:
            return custom_response(
                400,
                'Failed to disconnect. May be you are not the first admin connect to this OA',
            )    
    
    @action(detail=False, methods=['post'], url_path='oa-list')
    def get_oa_list_v2(self, request, *args, **kwargs) -> Response:
        """
        API get Zalo OA list
        """
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)

        oa_owner_queryset = get_oa_queryset_by_user_id(user_header)
        oa_owner_serializers = FanPageSerializer(oa_owner_queryset, many=True)
        
        # Verify access token expiration of active Zalo OA  
        for item in oa_owner_serializers.data:
            data = dict(item)
            
            oa_id = data.get('page_id')
            oa_model = FanPage.objects.filter(
                type='zalo',
                page_id=oa_id
            ).first()
            
            if data.get('is_deleted') or oa_model.access_token_page == 'Invalid':
                continue
            
            access_token = oa_model.access_token_page
            refresh_token = oa_model.refresh_token_page
            oa_info = zalo_oa_auth.get_oa_info(access_token)
            if not oa_info or oa_info.get('message') != 'Success':
                # Call refresh Zalo OA token
                oa_token = zalo_oa_auth.get_oa_token(refresh_token=refresh_token)
                if not oa_token or oa_token.get('message') == 'Failure':
                    oa_model.is_active = False
                    oa_model.last_subscribe = timezone.now()
                    oa_model.save()
                else:
                    oa_model.access_token_page = oa_token.get('data').get('access_token')
                    oa_model.refresh_token_page = oa_token.get('data').get('refresh_token')
                    oa_model.is_active = True
                    oa_model.last_subscribe = timezone.now()
                    oa_model.save()
            else:
                oa_data = oa_info.get('data')
                oa_model.name = oa_data.get('name')
                oa_model.avatar_url = oa_data.get('avatar_url')
                oa_model.is_active = True
                oa_model.save()
                
        return custom_response(
            message='Get OA list successfully', 
            data=oa_owner_serializers.data
        )
    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh_token(self, request, *args, **kwargs) -> Response:
        """
        API refresh tokens
        """
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)
        serializer = ZaloConnectPageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        oa_id = serializer.data.get('oa_id')
        queryset = FanPage.objects.filter(
            page_id=oa_id,
            is_deleted=False,                               
        ).first()
        
        if queryset:
            if not queryset.user_id == user_header:
                return custom_response(
                    400,
                    'Failed to reconnect. May be you are not the first admin connect to this OA',
                )

            refresh_token_page = queryset.refresh_token_page

            if refresh_token_page:
                oa_token = zalo_oa_auth.get_oa_token(refresh_token=refresh_token_page)
                
                if not oa_token or oa_token.get('message') == 'Failure':
                    queryset.is_active = False
                    queryset.last_subscribe = timezone.now()
                    queryset.save()
                    return custom_response(400, 'Failed to authorize Zalo OA')

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

    @action(detail=False, methods=['post'], url_path='setting-chat')
    def setting_chat_zalo(self, request, *args, **kwargs) -> Response:
        sz = SettingChatZaloSerializer(data = request.data)
        sz.is_valid(raise_exception=True)
        user_header = get_user_from_header(request.headers)
        find_page = FanPage.objects.filter(page_id=sz.data.get('page_id')).first()
        if not find_page:
            return custom_response(400, 'Not Find Zalo OA', [])
        if find_page.user_id != user_header:
            return custom_response(400, 'User Does Not Permission Setting Zalo OA', [])
        if sz.data.get('setting_chat') == constants.SETTING_CHAT_ONLY_ME:
            find_page.setting_chat = constants.SETTING_CHAT_ONLY_ME
        elif sz.data.get('setting_chat') != constants.SETTING_CHAT_ONLY_ME:
            find_page.setting_chat = sz.data.get('setting_chat')
            # if not sz.data.get('group_user'):
            #     return custom_response(400, 'Group User Is Not Valid', [])
            # find_page.group_user = sz.data.get('group_user')
        find_page.save()
        return custom_response(200, 'Setting Chat Zalo Success', [])

    @action(detail=True, methods=['post'], url_path='get-setting-chat')
    def get_setting_chat_zalo(self, request, pk, *args, **kwargs) -> Response:
        user_header = get_user_from_header(request.headers)
        find_page = FanPage.objects.filter(page_id = pk, user_id = user_header).first()
        if not find_page:
            return custom_response(400, 'Not Find Zalo OA', [])
        result = {
            "setting_chat": find_page.setting_chat
        }
        return custom_response(200, 'Get Setting Chat Success', result)

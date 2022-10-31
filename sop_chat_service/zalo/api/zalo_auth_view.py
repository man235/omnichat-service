from django.utils import timezone
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
                type='zalo'
            ).first()
            
            # Verify the first Zalo OA owner
            if queryset:
                is_existing_oa = True
                if not queryset.user_id == user_header:
                    return custom_response(
                        400,
                        'Zalo OA is connected. May be you are not the first admin connect to this OA',
                    )
            else:
                is_existing_oa = False
                
            oa_auth_sz = ZaloAuthenticationSerializer(data=request.data)
            oa_auth_sz.is_valid(raise_exception=True)
            oa_token = zalo_oa_auth.get_oa_token(
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
                return custom_response(400, oa_info.get('error'))
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
                        'is_deleted': False,
                        'created_by': user_header,
                        'last_subscribe': str(timezone.now())
                    }
                    oa_sz = FanPageSerializer(data=oa_data_bundle)

                    if oa_sz.is_valid(raise_exception=True):                                        
                        if not is_existing_oa:
                            oa_model = oa_sz.create(oa_data_bundle)
                        else:
                            oa_model = oa_sz.update(queryset, oa_data_bundle)
                        
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
        
        # The list uses for gathering all oa_id that request user is a owner
        oa_id_owner_list = []
        
        oa_queryset_by_user_id = FanPage.objects.filter(
            type='zalo',
            is_deleted=False,
            user_id=user_header
        )
        if oa_queryset_by_user_id.exists():
            for oa in oa_queryset_by_user_id:
                oa_id_owner_list.append(oa.page_id)
                    
        room_queryset_by_user_id = Room.objects.filter(
            Q(type='zalo') &
            Q(page_id__is_deleted=False) &
            (Q(user_id=user_header) | Q(admin_room_id=user_header)),
        ).distinct()
        if room_queryset_by_user_id.exists():
            for room in room_queryset_by_user_id:
                if room.page_id:
                    oa_id_owner_list.append(room.page_id.page_id)
        
        oa_owner_queryset = FanPage.objects.filter(
            type='zalo',
            page_id__in=oa_id_owner_list
        )
        oa_owner_serializers = FanPageSerializer(oa_owner_queryset, many=True)
        
        # Verify access token expiration of active Zalo OA  
        for item in oa_owner_serializers.data:
            data = dict(item)

            if not data.get('is_active') or data.get('is_deleted'):
                continue
            
            oa_id = data.get('page_id')
            oa_model = FanPage.objects.filter(type='zalo', page_id=oa_id).first()
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
            if not sz.data.get('group_user'):
                return custom_response(400, 'Group User Is Not Valid', [])
            find_page.group_user = sz.data.get('group_user')
        find_page.save()
        return custom_response(200, 'Setting Chat Zalo Success', [])

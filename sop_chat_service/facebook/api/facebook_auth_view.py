from django.utils import timezone
import requests
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework import permissions, status
from django.conf import settings
from sop_chat_service.app_connect.models import Attachment, FanPage, Message, Room
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer
from sop_chat_service.facebook.serializers.facebook_auth_serializers import FacebookAuthenticationSerializer, FacebookConnectPageSerializer, DeleteFanPageSerializer
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from core import constants
import logging
import time
logger = logging.getLogger(__name__)


class FacebookViewSet(viewsets.ModelViewSet):
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = FacebookAuthenticationSerializer

    def list(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        pages = FanPage.objects.filter(user_id=user_header, type=constants.FACEBOOK,is_deleted= False)
        sz = FanPageSerializer(pages, many=True)
        return custom_response(200, "Get list page successfully", sz.data)

    @action(detail=False, methods=["POST"], url_path="list-page")
    def get_page(self, request, *args):
        user_header = get_user_from_header(request.headers)
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        graph_api = settings.FACEBOOK_GRAPH_API
        # try:
        query = {'redirect_uri': sz.data['redirect_url'], 'code': sz.data['code'],
                    'client_id': settings.FACEBOOK_APP_ID, 'client_secret': settings.FACEBOOK_APP_SECRET}
        access_response = requests.get(f'{graph_api}/oauth/access_token', params=query)
        if access_response.status_code == 200:
            page_query = {'access_token': access_response.json()['access_token']}
            me = requests.get(f'{graph_api}/me', params=page_query)
            fb_user_id= me.json()['id']
            page_response = requests.get(f'{graph_api}/me/accounts', params=page_query)
            if page_response.status_code == 200:
                data = page_response.json()
                id = []
                if  not data['data']:
                    return custom_response(400, "List Page Is Null", [])
                else:
                    
                    for item in data['data']:
                        page = FanPage.objects.filter(type='facebook',page_id=item['id'],user_id=user_header,fanpage_user_id=fb_user_id).first()
                        id.append(item['id'])
                        avt_id = item['id']
                        if page is None:
                            FanPage.objects.create(
                                page_id=item['id'], name=item['name'], access_token_page=item['access_token'],
                                avatar_url=f'{graph_api}/{avt_id}/picture',
                                user_id=user_header,fanpage_user_id=fb_user_id,
                                is_deleted=False
                            )
                        else:
                            page.access_token_page=item['access_token']
                            page.name=item['name']
                            page.avatar_url=f'{graph_api}/{avt_id}/picture'
                            page.is_deleted=False
                            page.save()
                page_remove = FanPage.objects.filter(user_id=user_header,fanpage_user_id=fb_user_id,type='facebook').exclude(page_id__in=id )
                for item in page_remove:
                    item.is_active = False
                    item.is_deleted=True
                    item.access_token_page = ''
                    item.save()
                    
                return custom_response(200, "Get list page success", [])
            else:
                return custom_response(500, "INTERNAL_SERVER_ERROR", [])
        else:
            return custom_response(500, "a", [])
        # except Exception:
        #     return custom_response(500, "INTERNAL_SERVER_ERROR", [])

    @action(detail=False, methods=["POST"], url_path="page/subscribe")
    def subscribe_page(self, request, *args):
        logger.debug(f'headers ----------------- {request.headers}')
        user_header = get_user_from_header(request.headers)
        sz = FacebookConnectPageSerializer(data=request.data)
        if sz.is_valid(raise_exception=True):
            graph_api = settings.FACEBOOK_GRAPH_API

            if sz.data.get('is_subscribe') == True:
                page_id = sz.data.get('page_id')
                try:
                    page = FanPage.objects.filter(type=constants.FACEBOOK, page_id=page_id, user_id=user_header).first()
                    if page.is_active:
                        return custom_response(400, "Error: This Fanpage Have Been Subscribe!!!", [])
                    query_field = {'subscribed_fields': settings.SUBCRIBE_FIELDS,
                                   'access_token': page.access_token_page}
                    response = requests.post(f'{graph_api}/{page_id}/subscribed_apps', data=query_field)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            if page:
                                if page.is_active:
                                    pass
                                page.is_active = True
                                page.last_subscribe = timezone.now()
                                page.save()
                            else:
                                pass
                        message = "Subscribed successfully"
                        sz = FanPageSerializer(page, many=False)
                        return custom_response(200, message, sz.data)
                    else:
                        return custom_response(500, "INTERNAL_SERVER_ERROR", [])
                except Exception:
                    return custom_response(500, 'INTERNAL_SERVER_ERROR', [])
            else:
                page_id = request.data.get('page_id')
                try:
                    page = FanPage.objects.filter(page_id=page_id, user_id=user_header).first()
                    if page:
                        if page.is_active:
                            page_id = page.page_id
                            query_field = {'access_token': page.access_token_page}
                            response = requests.delete(f'{graph_api}/{page_id}/subscribed_apps', data=query_field)
                            if response.status_code == 200:
                                data = response.json()
                                if data['success']:
                                    page.is_active = False
                                    page.last_subscribe = timezone.now()
                                    page.save()
                                else:
                                    pass
                                message = "Subscribed successfully"
                                sz = FanPageSerializer(page, many=False)
                                return custom_response(200, message, sz.data)
                            else:

                                message = response.json().get('error').get('message')

                                return custom_response(500, "INTERNAL_SERVER_ERROR", [])
                        else:
                            page_id = page.page_id
                            query_field = {'access_token': page.access_token_page}
                            response = requests.delete(f'{graph_api}/{page_id}/subscribed_apps', data=query_field)
                            if response.status_code == 200:
                                data = response.json()
                            else:
                                message = response.json().get('error').get('message')
                                return custom_response(500, "INTERNAL_SERVER_ERROR", [])
                    else:
                        pass
                except Exception as e:
                    return custom_response(500, 'INTERNAL_SERVER_ERROR', [])

    @action(detail=False, methods=['POST'], url_path='delete')
    def delete(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        sz = DeleteFanPageSerializer(data = request.data)
        sz.is_valid(raise_exception=True)
        graph_api = settings.FACEBOOK_GRAPH_API
        for id in sz.data['id']:
            page = FanPage.objects.filter(id=id, user_id=user_header).first()
            page_id = page.id
            if page.is_active == True:
                query_field = {'access_token': page.access_token_page}
                response = requests.delete(f'{graph_api}/{page_id}/subscribed_apps', data=query_field)
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        page.is_deleted= True
                        page.is_active = False
                    else:
                        pass
                else:
                    page.is_deleted= True
                    page.is_active = False
            else :
                page.is_deleted= True
                page.is_active = False
            page.save() 
        return custom_response(200,'Delete Pages Successfully',[])

    def destroy(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def create(self, request):
        pass

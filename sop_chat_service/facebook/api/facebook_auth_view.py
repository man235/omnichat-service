from datetime import datetime
import requests
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework import permissions, status
from django.conf import settings
from sop_chat_service.app_connect.models import FanPage
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer
from sop_chat_service.facebook.serializers.facebook_auth_serializers import FacebookAuthenticationSerializer, FacebookConnectPageSerializer, DeleteFanPageSerializer
from sop_chat_service.facebook.utils import custom_response
import logging
logger = logging.getLogger(__name__)


class FacebookViewSet(viewsets.ModelViewSet):
    queryset = FanPage.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = FacebookAuthenticationSerializer

    def list(self, request, *args, **kwargs):
        logger.debug(f'headers ----------------- {request.headers}')
        pages = FanPage.objects.all().exclude(last_subscribe=None)
        sz = FanPageSerializer(pages, many=True)
        return custom_response(200, "Get list page successfully", sz.data)

    @action(detail=False, methods=["POST"], url_path="list-page")
    def get_page(self, request, *args):
        logger.debug(f'headers ----------------- {request.headers}')
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        graph_api = settings.FACEBOOK_GRAPH_API
        try:
            query = {'redirect_uri': sz.data['redirect_url'], 'code': sz.data['code'],
                        'client_id': settings.FACEBOOK_APP_ID, 'client_secret': settings.FACEBOOK_APP_SECRET}

            access_response = requests.get(f'{graph_api}/oauth/access_token', params=query)
            logger.debug(f'access_response ------------------- {access_response.json()}')

            if access_response.status_code == 200:
                page_query = {'access_token': access_response.json()['access_token']}
                page_response = requests.get(f'{graph_api}/me/accounts', params=page_query)
                logger.debug(f'page_response ------------------- {page_response.json()}')
                if page_response.status_code == 200:
                    data = page_response.json()
                    for item in data['data']:
                        page = FanPage.objects.filter(page_id=item['id']).first()
                        id = item['id']
                        if page is None:
                            FanPage.objects.create(
                                page_id=item['id'], name=item['name'], access_token_page=item['access_token'],  avatar_url=f'{graph_api}/{id}/picture')
                        else:
                            pass

                    list_page = FanPage.objects.filter(is_active=False, last_subscribe=None)
                    pages = FanPageSerializer(list_page, many=True)

                    return custom_response(200, "Get list page success", pages.data)
                else:
                    return custom_response(500, "INTERNAL_SERVER_ERROR", [])
            else:
                return custom_response(500, "INTERNAL_SERVER_ERROR", [])
        except Exception:
            return custom_response(500, "INTERNAL_SERVER_ERROR", [])

    @action(detail=False, methods=["POST"], url_path="page/subscribe")
    def subscribe_page(self, request, *args):
        logger.debug(f'headers ----------------- {request.headers}')
        sz = FacebookConnectPageSerializer(data=request.data)
        if sz.is_valid(raise_exception=True):
            graph_api = settings.FACEBOOK_GRAPH_API

            if request.data.get('is_subscribe') == True:
                page_id = request.data.get('page_id')
                try:
                    page = FanPage.objects.filter(page_id=page_id).first()
                    query_field = {'subscribed_fields': settings.SUBCRIBE_FIELDS,
                                   'access_token': page.access_token_page}
                    response = requests.post(f'{graph_api}/{page_id}/subscribed_apps', data=query_field)
                    logger.debug(f'response ------------------- {response.json()}')
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            if page:
                                if page.is_active:
                                    pass
                                page.is_active = True
                                page.last_subscribe = datetime.now()
                                page.save()
                            else:
                                pass
                    else:
                        return custom_response(500, "INTERNAL_SERVER_ERROR", [])
                except Exception:
                    return custom_response(500, 'INTERNAL_SERVER_ERROR', [])
                message = "Subscribed successfully"

                return custom_response(200, message, [])
            else:
                page_id = request.data.get('page_id')
                try:
                    page = FanPage.objects.filter(page_id=page_id).first()
                    if page:
                        if page.is_active:
                            page_id = page.page_id
                            query_field = {'access_token': page.access_token_page}
                            response = requests.delete(f'{graph_api}/{page_id}/subscribed_apps', data=query_field)
                            if response.status_code == 200:
                                data = response.json()
                                if data['success']:
                                    page.is_active = False
                                    page.save()
                                else:
                                    pass
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
            message = "Unsubscribed successfully"
            return custom_response(200, message, [])

    @action(detail=False, methods=['POST'], url_path='delete')
    def delete(self, request, *args, **kwargs):
        sz = DeleteFanPageSerializer(data = request.data)
        sz.is_valid(raise_exception=True)
        for id in sz.data['id']:
            page = FanPage.objects.filter(id=id).first()
            if page:
                page.delete()
            else:
                continue      
        return custom_response(200,'Delete Pages Successfully',[])

    def destroy(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def create(self, request):
        pass
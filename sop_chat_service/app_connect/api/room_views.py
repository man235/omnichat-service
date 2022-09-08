from rest_framework import viewsets, permissions
from rest_framework.response import Response
from sop_chat_service.app_connect.serializers.room_serializers import (
    RoomMessageSerializer,
    SearchMessageSerializer,
    RoomSerializer,
    SearchMessageSerializer,
    ResponseSearchMessageSerializer,
    SortMessageSerializer
)
from django.utils import timezone
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
from sop_chat_service.app_connect.models import Room, Message
from sop_chat_service.facebook.utils import custom_response
from rest_framework.decorators import action
from django.utils import timezone
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.pagination import Pagination

class RoomViewSet(viewsets.ModelViewSet):
    pagination_class=Pagination

    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = (permissions.AllowAny, )

    def create(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        qs = Room.objects.filter()
        sz = RoomMessageSerializer(qs, many=True)
        ser_sort = SortMessageSerializer(data = request.data)
        ser_sort.is_valid(raise_exception=True)
        new_list = sorted(sz.data, key=lambda d: d['last_message']['created_at'])       # old -> new message in room
        if ser_sort.data.get('sort'):
            if ser_sort.data.get('sort').lower() == "new":
                new_list.reverse()
            return custom_response(200, "Get List Room Successfully", new_list)
        # if ser_sort.data.get('filter'):
        #     if 'type' in sz.data.get('filter'):
        #         type = request.query_params['type']
        #         qs = qs.filter(type=type)
        #     if 'status' in request.query_params:
        #         filter = request.query_params['status']
        #         if filter.lower() == 'waiting':
        #             qs = qs.filter(type=request.query_params['type'], approved_date__isnull=True)
        #         elif filter.lower() == 'processing':
        #             qs = qs.filter(type=request.query_params['type'],
        #                             approved_date__isnull=False, completed_date__isnull=True)
        #     elif 'status' in request.query_params:
        #         filter = request.query_params['status']
        #         if filter.lower() == 'waiting':
        #             qs = qs.filter(approved_date__isnull=True)
        #         elif filter.lower() == 'processing':
        #             qs = qs.filter(approved_date__isnull=False, completed_date__isnull=True)
        #     elif 'name' in request.query_params:
        #         qs = qs.filter(name__icontains=request.query_params['name'])
        return custom_response(200, "Get List Room Successfully", sz.data)
    
    @action(detail=False, methods=["POST"], url_path="search")
    def search_for_room(self, request, pk=None, *args, **kwargs):
        sz = SearchMessageSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        data = {}
        if sz.data.get('search'):
            qs_contact = Room.objects.filter(name__icontains=sz.data.get('search'))
            serializer_contact = ResponseSearchMessageSerializer(qs_contact, many=True)
            data['contact'] = serializer_contact.data
            qs_messages = Room.objects.filter(room_message__text__icontains=sz.data.get('search')).distinct()
            serializer_message = []
            for qs_message in qs_messages:
                count_mess = Message.objects.filter(text__icontains=sz.data.get('search'), room_id=qs_message).count()
                data_count_message = {
                    "user_id": qs_message.user_id,
                    "external_id": qs_message.external_id,
                    "name": qs_message.name,
                    "type": qs_message.type,
                    "room_id": qs_message.room_id,
                    "count_message": count_mess
                }
                serializer_message.append(data_count_message)
            data['messages'] = serializer_message
        return custom_response(200, "Search Successfully", data)

    @action(detail=True, methods=["POST"], url_path="complete")
    def complete_room(self, request, pk=None, *args, **kwargs):
        room = Room.objects.get(id=pk)
        room.completed_date =timezone.now()
        room.save()
        return custom_response(200,"Completed Room Successfully",[])
   
    def retrieve(self, request, pk=None):
        room = Room.objects.filter(id =pk).first()        
        if room:
            message = Message.objects.filter(room_id = room).order_by("-created_at")
            for item in message:
                if item.is_seen:
                    continue
                
                item.is_seen= timezone.now()
                item.save()
            paginator =  Pagination()
            page = paginator.paginate_queryset(message, request)
            sz= MessageSerializer(page  ,many=True)
            data = {
                'room_id' : room.room_id,
                'message':paginator.get_paginated_response(sz.data)
            }
            return custom_response(200,"Get Message Successfully",data)
        return custom_response(200,"Room is not Valid",[])
    
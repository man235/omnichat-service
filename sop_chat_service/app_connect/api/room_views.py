from crypt import methods
from rest_framework import viewsets, permissions
from django.db import connection
from sop_chat_service.app_connect.serializers.room_serializers import (
    RoomMessageSerializer,
    SearchMessageSerializer,
    RoomSerializer,
    SearchMessageSerializer,
    ResponseSearchMessageSerializer,
    SortMessageSerializer,
    UserInfoSerializer,
    CountAttachmentRoomSerializer
)
from django.utils import timezone
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
from sop_chat_service.app_connect.models import Room, Message, UserApp
from sop_chat_service.facebook.utils import custom_response
from rest_framework.decorators import action
from sop_chat_service.facebook.utils import custom_response
from django.db.models import Q
from sop_chat_service.utils.pagination import Pagination
from sop_chat_service.utils.filter import filter_room
from iteration_utilities import unique_everseen
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
        #   sort by room message
        if ser_sort.data.get('sort'):
            if ser_sort.data.get('sort').lower() == "new":
                new_list.reverse()
            return custom_response(200, "Get List Room Successfully", new_list)
        time = request.data.get('time',None)
        status = request.data.get('status',None)
        state = request.data.get('state',None)
        phone = request.data.get('phone',None)
        label = request.data.get('label',None)
        qs = Room.objects.all().order_by("-room_message__created_at")
        if time:
            qs = filter_room({"time":time},qs)
        if status:
            qs = filter_room({"status":status},qs)
        if state:
            qs = filter_room({"state":state},qs)
        if phone:
            qs = filter_room({"phone":phone},qs)
        if label:
            qs = filter_room({"label":label},qs)
        sz = RoomMessageSerializer(qs, many=True)
        list_data = []
        list_data=list(unique_everseen(sz.data))
        print(unique_everseen(sz.data))
        print(len(list_data))
        
        if list_data:
            # data['redis-cache-device-temperature-report'].sort(key=lambda x: x['reality_state'], reverse=True)
            limit_req = request.data.get('limit')
            offset_req = request.data.get('offset')
            if not limit_req or limit_req >= 0:
                limit_req = 10
            if not offset_req or offset_req >= 0:
                offset_req = 1
             
            _end = int(offset_req) * int(limit_req)
            _start = int(_end) - int(limit_req)
            data_result = {
                "count": len(list_data),
                "data": list_data[_start:_end]
            }
            return custom_response(200,"ok",data_result)
        return custom_response(200,"ok",ser_sort.data)
        #   filter by room message
        # if ser_sort.data.get('filter'):
        #     if ('type' in request.query_params and 'status' in request.query_params and
        #         'state' in request.query_params and 'phone' in request.query_params and 'label' in request.query_params):
        #         type_app = request.query_params['type']
        #         status = request.query_params['status']
        #         state = request.query_params['state']
        #         phone = request.query_params['phone']
        #         label = request.query_params['label']
                
        #         if filter.lower() == 'processing':
        #             qs = qs.filter(type=type_app, approved_date__isnull=True,)
        #         elif filter.lower() == 'done':
        #             qs = qs.filter(type=request.query_params['type'],
        #                             approved_date__isnull=False, completed_date__isnull=True)
        #         elif filter.lower() == 'all':
        #             qs = qs.filter(type=type_app, )
        #     if 'status' in request.query_params:
        #         filter = request.query_params['status']
        #         if filter.lower() == 'waiting':
        #             qs = qs.filter(type=request.query_params['type'], approved_date__isnull=True)
        #         elif filter.lower() == 'processing':
        #             qs = qs.filter(type=request.query_params['type'],
        #                             approved_date__isnull=False, completed_date__isnull=True)
        #     elif 'name' in request.query_params:
        #         qs = qs.filter(name__icontains=request.query_params['name'])
        # return custom_response(200, "Get List Room Successfully", sz.data)
    
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
                user_info = UserApp.objects.filter(external_id=qs_message.external_id).first()
                data_count_message = {
                    "user_id": qs_message.user_id,
                    "external_id": qs_message.external_id,
                    "name": qs_message.name,
                    "type": qs_message.type,
                    "room_id": qs_message.room_id,
                    "count_message": count_mess,
                    "avatar": user_info.avatar if user_info else None
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
        room = Room.objects.filter(room_id=pk).first()
        if not room:
            return custom_response(400,"Invalid room",[])    
        Message.objects.filter(room_id=room, is_seen__isnull=True, is_sender=False).update(is_seen=timezone.now())
        message = Message.objects.filter(room_id=room).order_by("-created_at")
        paginator = Pagination()
        page = paginator.paginate_queryset(message, request)
        sz= MessageSerializer(page, many=True)
        data = {
            'room_id' : room.room_id,
            'message':paginator.get_paginated_response(sz.data)
        }
        return custom_response(200,"Get Message Successfully",data)
    
    @action(detail=True, methods=["GET"], url_path="info")
    def info_user_room(self, request, pk=None, *args, **kwargs):
        room = Room.objects.filter(room_id=pk).first()
        if not room:
            return custom_response(400,"Invalid room",[])
        qs = UserApp.objects.filter(external_id=room.external_id).first()
        sz = UserInfoSerializer(qs,many=False)
        return custom_response(200,"User Info",sz.data)

    @action(detail=True, methods=["GET"], url_path="count-attachment")
    def count_attachment_room(self, request, room_id=None, *args, **kwargs):
        room = Room.objects.filter(room_id=room_id).first()
        if not room:
            return custom_response(400,"Invalid room",[])
        sz = CountAttachmentRoomSerializer(room, many=False)
        return custom_response(200,"User Info",sz.data)

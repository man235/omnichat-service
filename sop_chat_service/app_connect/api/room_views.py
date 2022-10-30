from crypt import methods
from rest_framework import viewsets, permissions
from sop_chat_service.app_connect.serializers.room_serializers import (
    InfoSerializer,
    RoomInfoSerializer,
    RoomMessageSerializer,
    RoomSerializer,
    ResponseSearchMessageSerializer,
    SearchRoomSerializer,
    SortMessageSerializer,
    UserInfoSerializer,
    CountAttachmentRoomSerializer,
    LabelSerializer
)
from django.utils import timezone
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
from sop_chat_service.app_connect.models import Room, Message, UserApp, Label
from sop_chat_service.facebook.utils import custom_response
from rest_framework.decorators import action
from django.db.models import Q
from sop_chat_service.utils.pagination import Pagination
from sop_chat_service.utils.filter import filter_room
from iteration_utilities import unique_everseen
from sop_chat_service.utils.pagination_data import pagination_list_data
from sop_chat_service.utils.request_headers import get_user_from_header


class RoomViewSet(viewsets.ModelViewSet):
    pagination_class=Pagination
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = (permissions.AllowAny, )

    def create(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        pass
    @action(detail=False, methods=["POST"], url_path="room-info")
    def room_info(self, request, *args, **kwargs):
        sz = RoomInfoSerializer(data= request.data,many=False)
        room = sz.validate(request ,request.data)
        sz = InfoSerializer(room, many=False)
        return custom_response(200,"success",sz.data)
    
    @action(detail=False, methods=["POST"], url_path="list-room")
    def list_room(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        qs = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)),
            completed_date__isnull=True, room_message__is_sender=False).distinct().order_by("-room_message__created_at")
        
        sz = RoomMessageSerializer(qs, many=True)
        ser_sort = SortMessageSerializer(data = request.data)
        ser_sort.is_valid(raise_exception=True)
        limit_req = request.data.get('limit', 10)
        offset_req = request.data.get('offset', 1)

        list_data = []
        filter_request = ser_sort.data.get('filter')
        if filter_request:
            data_filter = {
                "type":filter_request.get('type',None),
                "time" : filter_request.get('time',None),
                "status" : filter_request.get('status',None),
                "state" : filter_request.get('state',None),
                "phone" : filter_request.get('phone',None),
                "label" : filter_request.get('label',None)
            }
            qs = filter_room(data_filter, qs)
            sz = RoomMessageSerializer(qs, many=True)
        list_data = sz.data
        #   sort by room message
        if ser_sort.data.get('sort'):
            if ser_sort.data.get('sort').lower() == "old":
                list_data = sorted((sz.data), key=lambda d: d['last_message'].get('created_at'))       # old -> new message in room

        data_result = pagination_list_data(list_data, limit_req, offset_req)
        return custom_response(200,"success",data_result)
    
    @action(detail=False, methods=["POST"], url_path="search")
    def search_for_room(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        sz = SearchRoomSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        data = {}
        if sz.data.get('search'):
            qs_contact = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)),
                name__icontains=sz.data.get('search'), room_message__is_sender=False).distinct()
            serializer_contact = ResponseSearchMessageSerializer(qs_contact, many=True)
            data['contact'] = serializer_contact.data
            qs_messages = Room.objects.filter(room_message__text__icontains=sz.data.get('search'),user_id=user_header).distinct()
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
                    "avatar": user_info.avatar if user_info else None,
                    "fan_page_name": qs_message.page_id.name if qs_message.page_id else None,
                    "fan_page_avatar":qs_message.page_id.avatar_url if qs_message.page_id else None
                }
                serializer_message.append(data_count_message)
            data['messages'] = serializer_message
        return custom_response(200, "Search Successfully", data)

    @action(detail=True, methods=["POST"], url_path="complete")
    def complete_room(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.get(room_id=pk, user_id=user_header)
        if not room:
            return custom_response(400,"Invalid room",[])  
        room.completed_date =timezone.now()
        room.save()
        return custom_response(200,"Completed Room Successfully",[])

    def retrieve(self, request, pk=None):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)), room_id=pk).first()
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
    
    @action(detail=True, methods=["GET"], url_path="customer-info")
    def info_user_room(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)), room_id=pk).first()
        if not room:
            return custom_response(400,"Invalid room",[])
        room_sz = RoomSerializer(room,many=False)
        qs_customer = UserApp.objects.filter(external_id=room.external_id).first()
        sz_customer = UserInfoSerializer(qs_customer,many=False)
        qs_label = Label.objects.filter(room_id=room)
        sz_label = LabelSerializer(qs_label,many=True)
        data = {
            "customer_info": sz_customer.data,
            "label": sz_label.data,
            "room_info":room_sz.data,
            "fanpage_id": room.page_id.page_id if room.page_id else None,
            "external_id": sz_customer.data.get("external_id")
        }
        return custom_response(200,"User Info",data)

    @action(detail=True, methods=["GET"], url_path="count-attachment")
    def count_attachment_room(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)), room_id=pk).first()
        if not room:
            return custom_response(400,"Invalid room",[])
        sz = CountAttachmentRoomSerializer(room, many=False)
        return custom_response(200,"Count Attachment",sz.data)

    @action(detail=False, methods=["GET"], url_path="channel")
    def count_unseen_message_room(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        all_room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)))
        facebook = 0
        live_chat = 0
        zalo = 0
        for room in all_room:
            if room.type.lower() == 'facebook':
                count_message_unseen = Message.objects.filter(room_id=room, is_seen__isnull=True).count()
                facebook += count_message_unseen
            elif room.type.lower() == 'zalo':
                count_message_unseen = Message.objects.filter(room_id=room, is_seen__isnull=True).count()
                zalo += count_message_unseen
            elif room.type.lower() == 'livechat':
                count_message_unseen = Message.objects.filter(room_id=room, is_seen__isnull=True).count()
                live_chat += count_message_unseen
        data = {
            "total": facebook + zalo + live_chat,
            "facebook": facebook,
            "zalo": zalo,
            "live_chat": live_chat,
        }
        return custom_response(200,"Count Seen Message Channel",data)

from rest_framework import viewsets, permissions
from sop_chat_service.app_connect.serializers.room_serializers import (
    CompleteRoomSerializer,
    InfoSerializer,
    RoomInfoSerializer,
    RoomMessageSerializer,
    RoomSerializer,
    ResponseSearchMessageSerializer,
    SearchRoomSerializer,
    SortMessageSerializer,
    UserInfoSerializer,
    CountAttachmentRoomSerializer,
    LabelSerializer,
    RoomIdSerializer
)
from django.utils import timezone
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer,LogMessageSerializer,GetLogMessage
from sop_chat_service.app_connect.models import Room, Message, UserApp, Label,AssignReminder, FanPage,LogMessage
from sop_chat_service.facebook.utils import custom_response
from rest_framework.decorators import action
from django.db.models import Q
from sop_chat_service.utils.pagination import Pagination
from sop_chat_service.utils.filter import filter_room
from iteration_utilities import unique_everseen
from sop_chat_service.utils.pagination_data import pagination_list_data
from sop_chat_service.utils.request_headers import get_user_from_header
from django.db import connection
from sop_chat_service.utils.remove_accent import remove_accent  
from sop_chat_service.app_connect.models import Reminder
from sop_chat_service.app_connect.serializers.reminder_serializers import ReminderSerializer,AssignReminderSerializer,GetAssignReminderSerializer,DeactiveAssignReminderSerializer
from .message_facebook_views import connect_nats_client_publish_websocket
from core import constants
from core.utils import format_log_message
import asyncio, ujson
from sop_chat_service.app_connect.tasks import create_reminder_task



class RoomViewSet(viewsets.ModelViewSet):
    pagination_class=Pagination
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = (permissions.AllowAny, )

    def create(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        pass
    @action(detail=False, methods=["POST"], url_path="reminder")
    def get_reminder(self, request, *args, **kwargs):
        data = request.data
        user_header = get_user_from_header(request.headers)
        room= Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)),room_id = data.get('room_id',None)).first()
        if not room:
            return custom_response(400," Room id invalid",[])
        qs = AssignReminder.objects.filter(room_id = room).exclude(repeat_time = 0)
        sz = GetAssignReminderSerializer(qs,many=True)
        return custom_response(200,"success",sz.data)

    @action(detail=False, methods=["POST"], url_path="room-info")
    def room_info(self, request, *args, **kwargs):
        sz = RoomInfoSerializer(data= request.data,many=False)
        room = sz.validate(request ,request.data)
        sz = InfoSerializer(room, many=False)
        return custom_response(200,"success",sz.data)
    
    @action(detail=False, methods=["POST"], url_path="list-room")
    def list_room(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        qs = Room.objects.filter(
            (Q(user_id=user_header) | Q(admin_room_id=user_header)),
            room_message__is_sender=False).distinct().order_by("-room_message__created_at")
        sz = RoomMessageSerializer(qs, many=True)
        ser_sort = SortMessageSerializer(data = request.data)
        ser_sort.is_valid(raise_exception=True)
        limit_req = request.data.get('limit', 10)
        offset_req = request.data.get('offset', 1)

        list_data = []
        filter_request = ser_sort.data.get('filter')
        if filter_request:
            data_filter = {
                "page_id": filter_request.get('page_id', constants.ALL),
                "type": filter_request.get('type', None),
                "time" : filter_request.get('time', None),
                "status" : filter_request.get('status', None),
                "state" : filter_request.get('state', None),
                "phone" : filter_request.get('phone', None),
                "label" : filter_request.get('label', None)
            }

            qs = Room.objects.filter(
                (Q(user_id=user_header) | Q(admin_room_id=user_header)),
                room_message__is_sender=False,
            ).distinct().order_by("-room_message__created_at")
            
            if data_filter.get('page_id') != constants.ALL:
                oa_qs = FanPage.objects.filter(
                    page_id=data_filter.get('page_id'),
                    is_deleted=False
                ).first()
                qs = qs.filter(page_id=oa_qs)                

            qs = filter_room(data_filter, qs)
            
            sz = RoomMessageSerializer(qs, many=True)
        list_data = list(unique_everseen(sz.data))
        #   sort by room message
        if ser_sort.data.get('sort'):
            if ser_sort.data.get('sort').lower() == "old":
                list_data = sorted(list(unique_everseen(sz.data)), key=lambda d: d['last_message'].get('created_at'))       # old -> new message in room

        data_result = pagination_list_data(list_data, limit_req, offset_req)
        return custom_response(200,"success",data_result)
    
    @action(detail=False, methods=["POST"], url_path="search")
    def search_for_room(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        sz = SearchRoomSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        data = {}
        result=[]
        search = remove_accent(sz.data.get('search'))
        if sz.data.get('search') and not  sz.data.get('is_filter'):
            cursor = connection.cursor()
            cursor.execute('''
                    select room.id 
                    from public.app_connect_room room 
                	where un_accent(room.name) ~* '\y%s' 
                    and(room.user_id = '%s' 
                    or room.admin_room_id = '%s')
            '''%(search,user_header,user_header))
            rows = cursor.fetchall()
            for row in rows:
                result.append(row[0])
        else:
            ser_sort = SortMessageSerializer(data = request.data)
            ser_sort.is_valid(raise_exception=True)
            if sz.data.get('is_filter'):
                filter_request = ser_sort.data.get('filter')
                data_filter = {
                "page_id":filter_request.get('page_id',None),
                "type":filter_request.get('type',None),
                "time" : filter_request.get('time',None),
                "status" : filter_request.get('status',None),
                "state" : filter_request.get('state',None),
                "phone" : filter_request.get('phone',None),
                "label" : filter_request.get('label',None)
            }
            qs = Room.objects.filter(
                (Q(user_id=user_header) | Q(admin_room_id=user_header)),
                room_message__is_sender=False).distinct().order_by("-room_message__created_at")
            qs = filter_room(data_filter, qs)
            sz = RoomIdSerializer(qs, many=True)
            list_data=[]
            for item in sz.data:
                    list_data.append(item['id'])
            list_data = str(set(list_data)).replace("{", "(").replace("}", ")")
            cursor = connection.cursor()
            cursor.execute('''
                    select room.id 
                    from public.app_connect_room room 
                	where room.id in %s and 
                    un_accent(room.name) ~* '\y%s' 
                    and(room.user_id = '%s' 
                    or room.admin_room_id = '%s')
            '''%(list_data,search,user_header,user_header))
            rows = cursor.fetchall()
            for row in rows:
                result.append(row[0])
        qs_contact = Room.objects.filter(id__in=result, room_message__is_sender=False).distinct()
        serializer_contact = ResponseSearchMessageSerializer(qs_contact, many=True)
        data['contact'] = serializer_contact.data
        qs_messages = Room.objects.filter(user_id=user_header,room_message__is_sender=False,id__in = result).distinct()
        qs_messages = qs_messages.filter(room_message__text__icontains=search).distinct()
        serializer_message = []
        for qs_message in qs_messages:
            count_mess = Message.objects.filter(text__icontains=search, room_id=qs_message).count()
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
        sz = CompleteRoomSerializer(request.data)
        msg = ""
        subject_publish = f"{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room.room_id}"
        if sz.data.get("is_complete"):
            room.completed_date =timezone.now()
            room.status='completed'
            room.save()
            log_message = format_log_message(room, f'{constants.LOG_COMPLETED}', constants.TRIGGER_COMPLETED)
            asyncio.run(connect_nats_client_publish_websocket(subject_publish, ujson.dumps(log_message).encode()))
            msg = "Complete Room Successfully"
            
        else:
            room.completed_date = None
            room.status='processing'
            room.save()
            log_message = format_log_message(room, f'{constants.LOG_REOPENED}', constants.TRIGGER_REOPENED)
            asyncio.run(connect_nats_client_publish_websocket(subject_publish, ujson.dumps(log_message).encode()))
            msg = "Re-open Room Successfully"
        return custom_response(200,msg,[])

    def retrieve(self, request, pk=None):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)), room_id=pk).first()
        if not room:
            return custom_response(400,"Invalid room",[])    
        Message.objects.filter(room_id=room, is_seen__isnull=True).update(is_seen=timezone.now())
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
        qs_assign_reminder = AssignReminder.objects.filter(room_id = room,user_id = user_header).order_by('-created_at').first()
        assign_sz = GetAssignReminderSerializer(qs_assign_reminder,many=False)
        qs_label = Label.objects.filter(room_id=room)
        sz_label = LabelSerializer(qs_label,many=True)
        data = {
            "customer_info": sz_customer.data,
            "assign_reminder": assign_sz.data if assign_sz.data else None,
            "label": sz_label.data,
            "room_info":room_sz.data,
            "fanpage_id": room.page_id.page_id if room.page_id else None,
            "external_id": sz_customer.data.get("external_id"),
            "block_room": True if user_header == room.admin_room_id else False
        }
        Message.objects.filter(room_id=room).update(is_seen=timezone.now())
        return custom_response(200,"User Info",data)

    @action(detail=True, methods=["GET"], url_path="count-attachment")
    def count_attachment_room(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter((Q(user_id=user_header) | Q(admin_room_id=user_header)), room_id=pk).first()
        if not room:
            return custom_response(400,"Invalid room",[])
        sz = CountAttachmentRoomSerializer(room, many=False)
        return custom_response(200,"Count Attachment",sz.data)

    @action(detail=False, methods=["GET"], url_path="add-un-accent")
    def add_func(self, request, *args, **kwargs):
        cursor = connection.cursor()
        cursor.execute('''
                CREATE OR REPLACE FUNCTION un_accent(x text) RETURNS text AS
                $$
                DECLARE
                 cdau text; kdau text; r text;
                BEGIN
                 cdau = 'áàảãạâấầẩẫậăắằẳẵặđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶĐÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ';
                 kdau = 'aaaaaaaaaaaaaaaaadeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyaaaaaaaaaaaaaaaaadeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyy';
                 r = x;
                 FOR i IN 0..length(cdau)
                 LOOP
                 r = replace(r, substr(cdau,i,1), substr(kdau,i,1));
                 END LOOP;
                 RETURN r;  
                END;
                $$ LANGUAGE plpgsql;
        ''')
        return custom_response(200,"Count Attachment",[])

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
    
    @action(detail=False, methods=["POST"], url_path="assign-reminder")
    def assign_reminder(self, request, *args, **kwargs):
        sz =  AssignReminderSerializer(data=request.data)        
        room,reminder,user_header = sz.validate(request,request.data)
        assign= AssignReminder.objects.create(
            room_id = room,
            user_id = user_header,
            reminder_id= reminder,
            title= reminder.title,
            unit=reminder.unit,
            time_reminder= reminder.time_reminder,
            repeat_time= reminder.repeat_time,
        )
        assign.save()
        assign_sz= GetAssignReminderSerializer(assign)
        log_message = format_log_message(room, assign.title, constants.TRIGGER_REMINDED)
        subject_publish = f"{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room.room_id}"
        asyncio.run(connect_nats_client_publish_websocket(subject_publish, ujson.dumps(log_message).encode()))
        create_reminder_task.delay(assign.id, int(assign.repeat_time))
        return custom_response(200,"Assign Reminder Successfully",assign_sz.data)
    
    @action(detail=False, methods=["POST"], url_path="deactive-noti")
    def deactive(self, request, *args, **kwargs):
        sz =  DeactiveAssignReminderSerializer(data=request.data)    
        room,assign,user_header = sz.validate(request,request.data)    
        assign.is_active_reminder = False
        assign.save()
        assign_sz= GetAssignReminderSerializer(assign)
        return custom_response(200,"Close Noti Successfully",assign_sz.data)
    
    @action(detail=False, methods=["POST"], url_path="remove-assign-reminder")
    def remove_assign(self, request, *args, **kwargs):
        sz =  DeactiveAssignReminderSerializer(data=request.data)    
        room,assign,user_header = sz.validate(request,request.data)    
        assign.is_active_reminder = False
        assign.delete()
        return custom_response(200,"Delete Assign Reminder Successfully",[])
    @action(detail=False, methods=["POST"], url_path="list-log")
    def list_log(self, request, *args, **kwargs):
        sz =  GetLogMessage(data=request.data)    
        room,user_header = sz.validate(request,request.data)
        parent_log = LogMessage.objects.filter(room_id = room.room_id).order_by('created_at').first()
        parent_log_sz = LogMessageSerializer(parent_log) 
        logs = LogMessage.objects.filter(room_id = room.room_id,log_type="").exclude(id = parent_log.id).order_by('-created_at')
        logs_sz = LogMessageSerializer(logs) 
        data ={
            "parent_log" : parent_log_sz.data,
            "logs": logs_sz
        }
        return custom_response(200,"Get List Log Successfully",data)
    
    

from datetime import datetime, timedelta
from sop_chat_service.app_connect.models import Room
from django.db.models.query_utils import Q

def filter_room(data, room : Room):
    time =data.get('time',None)
    status = data.get('status',None)
    state = data.get('state',None)
    phone = data.get('phone',None)
    label = data.get('label',None)
    if data:
        if time:
            start_date=datetime.today().replace(hour=0, minute=0, second=0)
            end_date=datetime.today()
            if time == 'today':
                pass
            elif time == 'yesterday':
                start_date = start_date - timedelta(days=1)
            elif time =='a_week_ago':
                start_date = start_date - timedelta(days=7)
            elif time =='a_month_ago':
                start_date = start_date - timedelta(days=30)
            elif time =='in_month':
                start_date = start_date.replace(day=1)
            # room = room.filter(room_message__timestamp__range=[start_date.timestamp(),end_date.timestamp()])
            room = room.filter(room_message__created_at__range = [start_date, end_date])
        if status:
            if status == "all":
                # room = room.all()
                room = room.filter(Q(status="processing") | Q(status="completed"))
            elif status == "processing":
                room = room.filter(status="processing")
            elif status == 'completed':
                room = room.filter(status="completed")
        if state:
            if state == 'unread':
                room = room.filter(room_message__is_seen__isnull =True)
            if state == 'not_answer':
                room = room.filter(room_message__is_sender = False, room_message__is_seen__isnull=True)
                # room = room.filter((Q(room_message__is_sender = False) & Q(room_message__is_seen__isnull=True)))
            if state == 'remind':
                room = room.filter(room_reminder__isnull=False)
        return room
    else:
        return room

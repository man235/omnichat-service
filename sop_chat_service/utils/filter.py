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
            startdate=datetime.today()
            enddate=datetime.today()
            if time == 'today':
                enddate= datetime.today()
                startdate = datetime.now().replace(hour=0, minute=0, second=0)
            elif time == 'yesterday':
                enddate = datetime.now().replace(hour=0, minute=0, second=0)
                startdate = enddate - timedelta(days=1)
                
            elif time =='a-week-ago':
                enddate = datetime.today()
                startdate = startdate - timedelta(days=7)
            elif time =='a-month-ago':
                enddate = datetime.today()
                startdate = startdate - timedelta(days=30)
            elif time =='in-month':
                enddate = datetime.today()
                startdate =datetime.now().replace(day=1) 
            
            room = room.filter(room_message__timestamp__range=[startdate.timestamp(),enddate.timestamp()])
            return room
        if status:
            if status == "all":
                room = room.all()
            elif status == "processing":
                room = room.filter(status="processing")
            elif status == 'completed':
                room = room.filter(status="completed")
            return room
        if state:
            if state == 'unread':
                room = room.filter(room_message__is_seen__isnull =True)
            if state == 'not_answer':
                room = room.filter((Q(room_message__is_sender = False) & Q(room_message__is_seen__isnull=True)))
            if state =='remind':
                room = room.filter(room_reminder__isnull=False)
        return room

    else:
        return room

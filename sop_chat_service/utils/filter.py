from datetime import datetime, timedelta
from sop_chat_service.app_connect.models import Room,FanPage,Label
from django.db.models.query_utils import Q

def filter_room(data, room : Room):
    page_id =data.get('page_id',None)
    time =data.get('time',None)
    status = data.get('status',None)
    state = data.get('state',None)
    phone = data.get('phone',None)
    label = data.get('label',None)
    type =data.get('type',None)
    if data:
        if page_id:
            if str(page_id).lower() == "all":
                pass
            else:
                page= FanPage.objects.filter(page_id=int(page_id)).first()
                room = room.filter(page_id =page)
        if type:
            if type.lower() == "all":
                pass
            else:
                room = room.filter(type=type)
        if time:
            start_date=datetime.today().replace(hour=0, minute=0, second=0)
            end_date=datetime.today()
            if time == 'today':
                pass
            elif time == 'yesterday':
                end_date=datetime.today().replace(hour=0, minute=0, second=0)
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
                pass
            elif status == "processing":
                room = room.filter(status="processing")
            elif status == 'completed':
                room = room.filter(status="completed")
        if state:
            for item in state :
                if item == 'unread':
                    room = room.filter(room_message__is_seen__isnull =True)
                if item == 'not_answer':
                    room = room.filter(room_message__is_sender = False, room_message__is_seen__isnull=True)
                    # room = room.filter((Q(room_message__is_sender = False) & Q(room_message__is_seen__isnull=True)))
                if item == 'remind':
                    room = room.filter(room_reminder__isnull=False)
        if label:
            if label['type'] == 'all':
                for r in room :
                    for item in label['label']:
                        exclude_room = room.filter(id=r.id,room_label__label_id__in = [str(item)])
                        if not exclude_room:
                            room = room.filter(~Q(id = r.id))                            
            elif label['type'] == 'exclude':
                room = room.filter(~Q(room_label__label_id__in = label['label']),)
            elif label['type'] == 'contain':
                room = room.filter(room_label__label_id__in = label['label'])
                
        return room
    
    else:
        return room

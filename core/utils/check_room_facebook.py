from sop_chat_service.app_connect.models import FanPage, Room
import datetime
from django.utils import timezone
from asgiref.sync import sync_to_async


@sync_to_async
def check_room_facebook(data):
    check_fanpage = FanPage.objects.filter(page_id=data.get("recipientId")).first()
    if not check_fanpage or not check_fanpage.is_active:
        return None
    check_room = Room.objects.filter(page_id=check_fanpage.id, external_id=data['senderId']).first()
    if not check_room or check_room.completed_date:
        new_room = Room(
            page_id = check_fanpage,
            external_id = data['senderId'],
            # user_id = data.get("senderId"),        # User SSO
            # name = "user_app.name",
            approved_date = timezone.now(),
            type = "facebook",
            completed_date = None,
            conversation_id = ""
        )
        new_room.save()
        return new_room
    else:
        return check_room

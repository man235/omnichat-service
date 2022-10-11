from datetime import datetime, timedelta
import imp
import uuid
from sop_chat_service.app_connect.models import Message, Room
from sop_chat_service.live_chat.models import LiveChat
from django.utils import timezone
from core.schema import  NatsChatMessage
import logging
logger = logging.getLogger(__name__)


async def check_room_live_chat(data: NatsChatMessage):

    live_chat = LiveChat.objects.filter(id =data.recipientId).first()
    if not live_chat or not live_chat.is_active:
        logger.debug(f' NOT FIND Live Chat FROM DATABASE -------------------------')
        return None
    start_date=datetime.strptime(str(datetime.today() - timedelta(days=1)).split(".")[0],'%Y-%m-%d %H:%M:%S')
    end_date=datetime.today()
    check_room = Room.objects.filter(type='livechat',external_id=data.senderId,user_id=live_chat.user_id).order_by("-created_at").first()
    if check_room and (end_date - check_room.created_at).total_seconds()/3600 < 24:
        count_message = Message.objects.filter(room_id = check_room)
        if count_message == 0:
            return check_room
        else:
            check_room = Room.objects.filter(type='livechat',external_id=data.senderId,user_id=live_chat.user_id,
                    room_message__is_sender = False,room_message__created_at__range = [start_date, end_date]).first()
    if not data.room_id:
        logger.debug("MISSING ROOM_ID OF LIVE CHAT ********************** ")
    if not check_room or check_room.completed_date:
        new_room = Room(
            external_id = data.senderId,
            name = "unknown",
            approved_date = timezone.now(),
            type = "livechat",
            completed_date = None,
            conversation_id = "",
            room_id = data.room_id,
            user_id=live_chat.user_id,
        )
        new_room.save()
        return new_room
    else:
        return check_room

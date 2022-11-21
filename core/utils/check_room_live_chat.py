from datetime import datetime, timedelta
import imp
import uuid
from core.celery.call_to_user_service import log_elk
from core.utils.format_elastic_log import ELK_LOG_ACTION, format_elk_log
from sop_chat_service.app_connect.models import Message, Room
from sop_chat_service.live_chat.models import LiveChat
from django.utils import timezone
from core.schema import  NatsChatMessage
import logging
logger = logging.getLogger(__name__)
from core.celery import create_log_time_message



async def check_room_live_chat(data: NatsChatMessage):
    live_chat = LiveChat.objects.filter(id =data.recipientId).first()
    if not live_chat or not live_chat.is_active:
        logger.debug(f' NOT FIND Live Chat FROM DATABASE -------------------------')
        return None
    start_date=datetime.strptime(str(datetime.today() - timedelta(days=1)).split(".")[0],'%Y-%m-%d %H:%M:%S')
    end_date=datetime.today()
    check_room = Room.objects.filter(type='livechat',external_id=data.senderId).order_by("-created_at").first()
    if check_room and (end_date - check_room.created_at).total_seconds()/3600 < 24:
        if not check_room.user_id:
            check_room.user_id= live_chat.user_id
            check_room.save()
        return check_room
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
        create_log_time_message.delay(new_room.room_id)

        return new_room
    else:
        return check_room

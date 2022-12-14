from core.celery.call_to_user_service import log_elk
from core.utils.format_elastic_log import ELK_LOG_ACTION, format_elk_log
from sop_chat_service.app_connect.models import FanPage, Room, UserApp
from .api_facebook_app import get_user_info
from django.utils import timezone
from core.schema import  NatsChatMessage
from core.celery import celery_task_verify_information,create_log_time_message,re_open_room
from core import constants
from .format_data_celery import celery_format_data_verify_customer
import logging
import time
from core.stream.redis_connection import redis_client

logger = logging.getLogger(__name__)


async def check_room_facebook(data: NatsChatMessage):
    check_fanpage = FanPage.objects.filter(page_id=data.recipientId, is_active=True).first()
    if not check_fanpage or not check_fanpage.is_active:
        logger.debug(f' NOT FIND FANPAGE FROM DATABASE -------------------------')
        return None
    user_app = UserApp.objects.filter(external_id=data.senderId).first()
    if not user_app:
        res_user_app = get_user_info(data.senderId, check_fanpage.access_token_page)
        if not res_user_app:
            logger.debug(f' NOT FIND USER APP FROM FACEBOOK ------------------------- {res_user_app}')
            return
        user_app = UserApp.objects.create(
            # user_id = res_user_app.get('profile_pic'),
            external_id = data.senderId,
            name = res_user_app.get('last_name') + " " + res_user_app.get('first_name'),
            avatar = res_user_app.get('profile_pic'),
            email = res_user_app.get(''),
            phone = res_user_app.get(''),
            gender = res_user_app.get('gender')
        )
    check_room = Room.objects.filter(page_id=check_fanpage.id, external_id=data.senderId,user_id=check_fanpage.user_id).first()
    if not check_room:
        new_room = Room(
            page_id = check_fanpage,
            external_id = data.senderId,
            name = user_app.name,
            approved_date = timezone.now(),
            type = "facebook",
            completed_date = None,
            conversation_id = "",
            room_id = f'{check_fanpage.id}{data.senderId}',
            user_id=check_fanpage.user_id,
        )
        new_room.save()
        data = await celery_format_data_verify_customer(user_app, new_room)
        celery_task_verify_information.delay(data)
        create_log_time_message.delay(new_room.room_id)

        elk_log = format_elk_log(ELK_LOG_ACTION.get('HANDLE_MESSAGE'), new_room.room_id)
        log_elk.delay(elk_log=elk_log)

        return new_room
    elif check_room:
        last_msg = redis_client.hget(f'{constants.REDIS_LAST_MESSAGE_ROOM}{check_room.room_id}', constants.LAST_MESSAGE)
        if last_msg:
            if int(time.time() * 1000) - int(last_msg) >= 86400000:
                create_log_time_message.delay(check_room.room_id)

                elk_log = format_elk_log(ELK_LOG_ACTION.get('CHAT'), check_room.room_id)
                log_elk.delay(elk_log=elk_log)
        if check_room.completed_date:
            re_open_room.delay(check_room.room_id)

            elk_log = format_elk_log(ELK_LOG_ACTION.get('CUSTOMER_REOPEN'), check_room.room_id)
            log_elk.delay(elk_log=elk_log)

            check_room.completed_date = None
            check_room.status = 'processing'
            check_room.save()
            
        return check_room



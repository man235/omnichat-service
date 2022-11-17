from typing import Any
from sop_chat_service.app_connect.models import FanPage, Room, UserApp
from django.utils import timezone
from asgiref.sync import sync_to_async
from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_oa_follower
from sop_chat_service.app_connect.api.message_facebook_views import connect_nats_client_publish_websocket
from core.utils.format_log_message import format_data_log_message
from core.schema import NatsChatMessage
import ujson
import logging
from core.celery import create_log_time_message,re_open_room
from core import constants
import time
import asyncio
from core.stream.redis_connection import redis_client
from core import constants
from core.utils.distribute_new_chat import find_user_new_chat
from core.celery import create_log_time_message
from core import constants
import time
from core.utils.format_data_celery import celery_format_data_verify_customer
from core.celery import celery_task_verify_information


logger = logging.getLogger(__name__)


async def distribute_new_room_zalo(data: NatsChatMessage) -> Room:
    check_fanpage = FanPage.objects.filter(
        page_id=data.recipientId,
        is_active=True,
        type=constants.ZALO,
    ).first()
        
    if not check_fanpage:
        logger.debug(f' NOT FIND FROM DATABASE -------------------------')
        return None
    
    user_app = UserApp.objects.filter(
        external_id=data.senderId,
    ).first()

    if not user_app:
        logger.debug(f' NOT FIND USER ZALO APP FROM DATABASE ------------------------- ')
        # Find user from zalo oa: Anomynous or Follower
        zalo_app_user: dict = get_oa_follower(
            data.senderId,
            check_fanpage.access_token_page,
        )
            
        if zalo_app_user.get('message') == 'Success':
            # Follower
            logger.debug(f' ZALO OA`S FOLLOWER USER ------------------------- ')
            zalo_app_user_data: dict = zalo_app_user.get('data')

            # Define user gender
            gender: int = zalo_app_user_data.get('user_gender')
            if gender == 0:
                checked_gender = 'Others'
            elif gender == 1:
                checked_gender = 'Male'
            elif gender == 2:
                checked_gender = 'Female'
            else:
                checked_gender = 'Undefined'

            user_app = UserApp.objects.create(
                external_id = data.senderId,
                name = zalo_app_user_data.get('display_name'),
                avatar = zalo_app_user_data.get('avatar'),
                gender = checked_gender,
            )
        else:
            # Anonymous User
            logger.debug(f' ANONYMOUS USER ZALO ------------------------- ')
            user_app = UserApp.objects.create(
                external_id = data.senderId,
                name = f'Anonymous-{data.senderId}',
            )
    
    check_room = Room.objects.filter(
        page_id=check_fanpage,
        external_id=data.senderId
    ).first()
    if not check_room:
        result_new_user = await find_user_new_chat(data, check_fanpage)
        new_room_user = Room.objects.create(
            page_id = check_fanpage,
            external_id = data.senderId,
            name = user_app.name,
            approved_date = timezone.now(),
            type = constants.ZALO,
            conversation_id = "",
            completed_date = None,
            room_id = f'{check_fanpage.id}{data.senderId}',
            user_id = result_new_user.get('staff'),
            admin_room_id = result_new_user.get('admin') if check_fanpage.setting_chat != constants.SETTING_CHAT_ONLY_ME else None
        )
        if check_fanpage.setting_chat != constants.SETTING_CHAT_ONLY_ME:
            subject_publish = f"{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{new_room_user.room_id}"
            log_message = format_data_log_message(new_room_user, f'{new_room_user.admin_room_id} {constants.LOG_FORWARDED} {new_room_user.user_id}', constants.TRIGGER_COMPLETED)
            asyncio.run(connect_nats_client_publish_websocket(subject_publish, ujson.dumps(log_message).encode()))
        data = await celery_format_data_verify_customer(user_app, new_room_user)
        celery_task_verify_information.delay(data)
        create_log_time_message.delay(new_room_user.room_id)

        return new_room_user
    else:
        last_msg = redis_client.hget(f'{constants.REDIS_LAST_MESSAGE_ROOM}{check_room.room_id}', constants.LAST_MESSAGE)
        if last_msg:
            if int(time.time() * 1000) - int(last_msg) >= 86400000:
                create_log_time_message.delay(check_room.room_id)
        if check_room.completed_date:
            check_room.completed_date = None
            check_room.status = constants.PROCESSING
            check_room.save()
            re_open_room.delay(check_room.room_id)
        return check_room

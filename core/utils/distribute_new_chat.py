from typing import Tuple
# from core.stream.redis_client import RedisClient
from core.stream.redis_connection import redis_client
from core.schema import NatsChatMessage
from sop_chat_service.app_connect.models import FanPage
import ast
from core import constants

# redis_client  = RedisClient()


async def get_users_from_noc(chat_msg: NatsChatMessage, fanpage: FanPage):
    list_user_new_chat = []
    get_list_user_noc = []
    if fanpage.setting_chat == constants.SETTING_CHAT_ONLY_ME:
        get_list_user_noc = [fanpage.user_id]
    else:
        get_list_user_noc = fanpage.group_user
    get_list_user_redis = redis_client.get(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{chat_msg.recipientId}')
    if not get_list_user_redis:
        list_user_new_chat = get_list_user_noc
        redis_client.set(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{chat_msg.recipientId}', str(list_user_new_chat))

    else:
        list_user_redis = ast.literal_eval(get_list_user_redis.decode())
        if not set(get_list_user_noc) == set(list_user_redis):
            list_user_new_chat = get_list_user_noc
            redis_client.set(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{chat_msg.recipientId}', str(list_user_new_chat))
        else:
            list_user_new_chat = list_user_redis
    return tuple(list_user_new_chat)


async def distribute_new_chat(chat_message: NatsChatMessage, admin: str, staffs: Tuple[str]):
    list_staff =  list(staffs)
    select_staff = list_staff.pop(0)

    list_staff.append(select_staff)
    redis_client.set(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{chat_message.recipientId}', str(list_staff))
    result = {
        "admin": admin,
        "staff": select_staff
    }
    return result


async def is_new_room(msg) -> bool:
    # control runner from this function
    return True


async def do_something_else(msg):
    print(f'do something else with {msg}')


async def find_user_new_chat(chat_message: NatsChatMessage, fanpage: FanPage):
    if not await is_new_room(chat_message):
        return await do_something_else(chat_message)

    zalo_users = await get_users_from_noc(chat_message, fanpage)
    result = await distribute_new_chat(chat_message, fanpage.user_id, zalo_users)
    return result

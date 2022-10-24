from typing import Tuple
from core.stream.redis_client import RedisClient
import ast
from core import constants

redis_client  = RedisClient()


async def get_users_from_noc(zalo_page_id: str):
    # call api to NOC get list user and admin of Zalo AO
    # get list user from redis
    # user = list api user from NOC subtract list redis ---> list user
    list_user_new_chat = []
    list_admin_new_chat = ['admin_01']
    get_list_user_noc = ['staff_01', 'staff_02', 'staff_03', 'staff_04', 'staff_05', 'staff_06']      # call api NOC
    get_list_user_redis = await redis_client.client.get(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{zalo_page_id}')
    if not get_list_user_redis:
        list_user_new_chat = get_list_user_noc
        await redis_client.client.set(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{zalo_page_id}', str(list_user_new_chat))

    else:
        list_user_redis = ast.literal_eval(get_list_user_redis)
        if not set(get_list_user_noc) == set(list_user_redis):
            list_user_new_chat = get_list_user_noc
            await redis_client.client.set(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{zalo_page_id}', str(list_user_new_chat))
        else:
            list_user_new_chat = list_user_redis
    # list_new_user = [user for user in get_list_user_noc if not user in list_user_redis]y
    # list_old_user = [user for user in get_list_user_noc if not user in list_new_user]
    # list_new_chat_user = list_new_user + list_old_user
    result = {
        'admins': tuple(list_admin_new_chat),
        'staffs': tuple(list_user_new_chat)
    }
    return result


async def distribute_new_chat(zalo_page_id, admins: Tuple[str], staffs: Tuple[str]):
    list_staff =  list(staffs)
    select_staff = list_staff.pop(0)

    list_staff.append(select_staff)
    await redis_client.client.set(f'{constants.REDIS_LIST_USER_NEW_CHAT}.{zalo_page_id}', str(list_staff))
    # return admins and selected staff
    return admins[0], select_staff


async def is_new_room(msg) -> bool:
    # control runner from this function
    return True


async def do_something_else(msg):
    print(f'do something else with {msg}')


async def find_user_new_chat(zalo_page_id):
    if not await is_new_room(zalo_page_id):
        return await do_something_else(zalo_page_id)

    zalo_users = await get_users_from_noc(zalo_page_id)
    message_to_users = await distribute_new_chat(zalo_page_id, zalo_users.get('admins'), zalo_users.get('staffs'))
    return message_to_users[0], message_to_users[1]

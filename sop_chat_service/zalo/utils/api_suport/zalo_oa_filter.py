from core import constants
from django.db.models import Q
from sop_chat_service.app_connect.models import FanPage, Room


def get_oa_queryset_by_user_id(user_header: str):
    # The list uses for gathering all oa_id that request user is a owner
    oa_id_owner_list = []
    
    oa_queryset_by_user_id = FanPage.objects.filter(
        type=constants.ZALO,
        is_deleted=False,
        user_id=user_header
    )
    if oa_queryset_by_user_id.exists():
        for oa in oa_queryset_by_user_id:
            oa_id_owner_list.append(oa.page_id)
                
    room_queryset_by_user_id = Room.objects.filter(
        Q(type=constants.ZALO) &
        Q(page_id__is_deleted=False) &
        (Q(user_id=user_header) | Q(admin_room_id=user_header)),
    ).distinct()
    if room_queryset_by_user_id.exists():
        for room in room_queryset_by_user_id:
            if room.page_id:
                oa_id_owner_list.append(room.page_id.page_id)

    oa_owner_queryset = FanPage.objects.filter(
        type=constants.ZALO,
        page_id__in=oa_id_owner_list
    )
    
    return oa_owner_queryset
    
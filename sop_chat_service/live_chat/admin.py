from django.contrib import admin

from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo, UserLiveChat

# Register your models here.


@admin.register(LiveChat)
class LiveChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_agent', 'is_active', 'color',"user_id"]


@admin.register(LiveChatRegisterInfo)
class RegisterInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'live_chat_id', 'type', 'name', 'value', 'required', 'is_active']
@admin.register(UserLiveChat)
class UserLiveChatAdmin(admin.ModelAdmin):
    list_display = ['id','room_id','title','value']
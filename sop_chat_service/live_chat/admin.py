from django.contrib import admin

from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo

# Register your models here.


@admin.register(LiveChat)
class LiveChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_agent', 'is_active', 'color']


@admin.register(LiveChatRegisterInfo)
class RegisterInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'live_chat_id', 'type', 'name', 'value', 'required', 'is_active']

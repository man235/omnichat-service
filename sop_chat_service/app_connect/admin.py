from django.contrib import admin
from sop_chat_service.app_connect.models import Attachment, FanPage, Message, Room, Label, Reminder, UserApp


# Register your models here.


@admin.register(FanPage)
class PageAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "page_id", "access_token_page",  "created_at", "is_active"]
    search_fields = ["name", "id"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["id", "page_id", "approved_date", "type", "conversation_id", "external_id", "user_id", "name", "room_id"]
    search_fields = ["name", "id"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "room_id", "text", "sender_id", "recipient_id", "created_at"]
    search_fields = ["text", "id"]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["id", "mid", "type", "url"]
    search_fields = ["id"]

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "room_id"]

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "unit", "room_id"]


@admin.register(UserApp)
class UserAppAdmin(admin.ModelAdmin):
    list_display = ["id", "external_id", "name", "avatar",  "email", "phone"]
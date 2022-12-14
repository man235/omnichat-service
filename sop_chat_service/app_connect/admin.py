from django.contrib import admin
from sop_chat_service.app_connect.models import Attachment, FanPage, Message, Room, Label, Reminder, ServiceSurvey, UserApp, LogMessage,AssignReminder


# Register your models here.


@admin.register(FanPage)
class PageAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "page_id", "access_token_page",  "created_at", "is_active"]
    search_fields = ["name", "id"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["id", "page_id", 'status',"approved_date", "type", "conversation_id", "external_id", "user_id", "name", "room_id"]
    search_fields = ["name", "id"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "room_id", "text", "sender_id", "recipient_id", "created_at","is_seen","is_sender"]
    search_fields = ["text", "id"]
    actions = ['check_is_seen']
    def check_is_seen(self, request, queryset):
        for qs in queryset:
            if qs.is_seen:
                qs.is_seen =None
                qs.save()
    


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["id", "mid", "type", "url"]
    search_fields = ["id"]
@admin.register(ServiceSurvey)
class ServiceSurveyAdmin(admin.ModelAdmin):
    list_display = ["id", "mid", "name", "value"]
    search_fields = ["id"]

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ["id", "label_id", "room_id"]

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "unit", "title",'time_reminder','repeat_time']
@admin.register(AssignReminder)
class AssignReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "unit", "title",'time_reminder','repeat_time']


@admin.register(UserApp)
class UserAppAdmin(admin.ModelAdmin):
    list_display = ["id", "external_id", "name", "avatar",  "email", "phone"]


@admin.register(LogMessage)
class LogMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "mid", "log_type", "message",  "room_id", "from_user", "to_user", "created_at"]
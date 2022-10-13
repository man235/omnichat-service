from re import sub
from django.db import models

from sop_chat_service.app_connect.models import Room
from sop_chat_service.live_chat.utils import file_size
from django.conf import settings
# Create your models here.


class LiveChat(models.Model):
    class LocationChoice(models.TextChoices):
        TOP_RIGHT = 'top_right'
        TOP_LEFT = 'top_left'
        BOTTOM_RIGHT = 'bottom_right'
        BOTTOM_LEFT = 'bottom_left'
    user_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    name_agent = models.CharField(max_length=255, null=True, blank=True)
    is_show_avatar = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(null=True, blank=True,validators=[file_size])
    avatar_url = models.CharField(null=True,blank=True,max_length=500)
    name_agent_active = models.BooleanField(default=True)
    is_popup = models.BooleanField(default=False)
    color = models.CharField(max_length=10, null=True, blank=True)
    icon = models.BooleanField(default=False)
    icon_content= models.CharField(max_length=255, null=True, blank=True)
    size = models.JSONField(null=True, blank=True)
    location = models.CharField(max_length=20, default=LocationChoice.TOP_RIGHT, choices=LocationChoice.choices)
    start_btn = models.CharField(max_length=255, null=True, blank=True)
    is_introduce_message = models.BooleanField(default=False)
    introduce_message = models.CharField(max_length=255, null=True, blank=True)
    is_start_message = models.BooleanField(default=False)
    start_message = models.CharField(max_length=255, null=True, blank=True)
    is_offline_message = models.BooleanField(default=False)
    offline_message = models.CharField(max_length=255, null=True, blank=True)
    is_registerinfor = models.BooleanField(default=False)
    script = models.CharField(max_length=1500, null=True, blank=True)

    def __str__(self):
        return str(self.id)
   
    def save(self, *args, **kwargs):
        if self.avatar:
            domain = settings.DOMAIN_MINIO_SAVE_ATTACHMENT
            sub_url = f"api/live_chat/chat_media/get_chat_media?name="
            # This code only happens if the objects is not in the database yet. Otherwise it would have pk
            self.avatar_url = str(domain)+str(sub_url)+str(self.avatar.name)
        else:
            self.avatar_url=None
        super(LiveChat, self).save(*args, **kwargs)

class LiveChatRegisterInfo(models.Model):
    live_chat_id = models.ForeignKey(LiveChat, on_delete=models.CASCADE,
                                     related_name='live_chat_id', null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    value = models.JSONField(null=True, blank=True)
    required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class UserLiveChat(models.Model):
    room_id = models.ForeignKey(Room, related_name='user_live_chat_room', null=True, blank=True,
                                on_delete=models.SET_NULL)   
    title = models.CharField(null=True,blank=True,max_length=255)
    value= models.CharField(null=True,blank=True,max_length=500)
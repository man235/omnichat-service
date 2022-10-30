from statistics import mode
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.postgres.fields import ArrayField
from sop_chat_service.utils.storages import upload_image_to
import time
from core import constants


class FanPage(models.Model):
    class Type(models.TextChoices):
        FACEBOOK = 'facebook'
        ZALO = 'zalo'
        LIVE_CHAT= 'livechat'
    page_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    access_token_page = models.CharField(max_length=12288, null=True, blank=True)
    refresh_token_page = models.CharField(max_length=12288, null=True, blank=True)
    avatar_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(null=True, default=False)
    app_secret_key = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_subscribe = models.DateTimeField(null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=30, default=Type.FACEBOOK,
                            choices=Type.choices)
    fanpage_user_id = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(null=True)
    group_user = ArrayField(models.CharField(max_length=200, null=True), blank=True, null=True)
    setting_chat = models.CharField(max_length=255, default=constants.SETTING_CHAT_ONLY_ME)

    def __str__(self):
        return str(self.id) + '-' + self.name+'-'+self.access_token_page


class UserApp(models.Model):
    # user_id = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)   # foreign key with user app
    name = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.URLField(max_length=10000,null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)


class Room(models.Model):
    class TypeRoomChoice(models.TextChoices):
        FACEBOOK = 'facebook'
        ZALO = 'zalo'
        LIVE_CHAT= 'livechat'

    class ApproachCustomerChoice(models.TextChoices):
        FACEBOOK = 'facebook'
        ZALO = 'zalo'
        GOOGLE = 'google'
    class Status(models.TextChoices):
        ALL='all'
        PROCESSING='processing'
        COMPLETED = 'completed'
        EXPIRED ="expired"
    class State(models.TextChoices):
        UNREAD='unread'
        NOT_ANSWER='not_answer'
        REMIND='remind'
    page_id = models.ForeignKey(FanPage, related_name='fanPage_room', null=True, blank=True,
                                on_delete=models.SET_NULL)
    external_id = models.CharField(max_length=255, null=True, blank=True)   # foreign key with user facebook
    user_id = models.CharField(max_length=255, null=True, blank=True)  # foreign key with user app
    name = models.CharField(max_length=255, null=True, blank=True)      # name of room chat --> may not need
    note = models.CharField(max_length=255, null=True, blank=True)      # note of room --> feature of note in room
    approved_date = models.DateTimeField(null=True, blank=True)     # approved date of room
    type = models.CharField(max_length=30, default=TypeRoomChoice.FACEBOOK,
                            choices=TypeRoomChoice.choices)     # type room --> tag type message
    completed_date = models.DateTimeField(null=True, blank=True)     # completed date of room
    conversation_id = models.CharField(max_length=255, null=True, blank=True)     # conversation id of room
    created_at = models.DateTimeField(auto_now_add=True)
    room_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, default=Status.PROCESSING,
                            choices=Status.choices)
    admin_room_id = models.CharField(max_length=255, null=True, blank=True)
    block_admin = models.BooleanField(null=True)

    def __str__(self):
        return str(self.id) + '-' + self.name


class Reminder(models.Model):
    class UnitChoice(models.TextChoices):
        DAY = 'day'
        HOUR = 'hour'
        MINUTE = 'minute'
        SECOND = 'second'

    room_id = models.ForeignKey(Room, related_name='room_reminder', null=True, blank=True,
                                on_delete=models.SET_NULL)     # foreign key with room
    unit = models.CharField(max_length=30, default=UnitChoice.HOUR, choices=UnitChoice.choices)     # unit of reminder
    title = models.CharField(max_length=255, null=True, blank=True)      # title for reminder
    time_reminder = models.IntegerField(null=True, blank=True)
    repeat_time = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Label(models.Model):
    room_id = models.ForeignKey(Room, related_name='room_label', null=True, blank=True,
                                on_delete=models.SET_NULL)     # foreign key with room
    name = models.CharField(max_length=255, null=True, blank=True)      # name contains content of label
    color = models.CharField(max_length=255, null=True, blank=True)      # color of content label
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    class ReactionChoice(models.TextChoices):
        LIKE = 'like'
        HAHA = 'haha'
        LOVE = 'love'
        WOW = 'wow'
        SAD = 'sad'
        ANGRY = 'angry'
        YAY = 'yay'

    uuid = models.CharField(max_length=255, null=True, blank=True)      # id unique of message
    room_id = models.ForeignKey(Room, related_name='room_message', null=True, blank=True,
                                on_delete=models.SET_NULL)     # foreign key with room
    fb_message_id = models.CharField(max_length=255, null=True, blank=True)      # message id of message
    sender_id = models.CharField(max_length=255, null=True, blank=True)      # id of sender message
    recipient_id = models.CharField(max_length=255, null=True, blank=True)      # id of recipient message
    reaction = models.CharField(max_length=30, choices=ReactionChoice.choices, null=True)     # unit of reminder
    is_forward = models.BooleanField(null=True, default=False)  # forward message?
    reply_id = models.IntegerField(null=True, blank=True)      # mid reply of message
    text = models.TextField(null=True, blank=True)      # content type text of message
    sender_name = models.CharField(max_length=255, null=True, blank=True)   # name of send message
    is_seen = models.DateTimeField(null=True, blank=True)     # seen message?
    # unsend_for_everyone = models.BooleanField(null=True, blank=True)    # message un-send for everyone
    # sender message is user app or employee? if true=> user app, false=> employee
    is_sender = models.BooleanField(null=True, default=False)
    remove_for_you = models.BooleanField(null=True, blank=True)     # message removed with me
    created_at = models.DateTimeField(auto_now_add=True)    # time create message
    timestamp = models.FloatField(null=True,blank=True)


class Attachment(models.Model):
    mid = models.ForeignKey(Message, related_name='message_id', null=True, blank=True,
                            on_delete=models.SET_NULL)     # foreign key with message
    attachment_id = models.CharField(max_length=255, null=True, blank=True)      # id of attachment
    file = models.FileField(blank=True, null=True, upload_to=upload_image_to)
    type = models.CharField(max_length=255, null=True, blank=True)      # type of attachment
    url = models.CharField(max_length=500, null=True, blank=True)      # url of attachment
    name = models.CharField(max_length=500, null=True, blank=True)      # name of attachment
    size = models.IntegerField(null=True, blank=True)

class ServiceSurvey(models.Model):
    mid = models.ForeignKey(Message, related_name='service_message_id', null=True, blank=True,
                            on_delete=models.SET_NULL)     # foreign key with message
    
    name = models.CharField(max_length=500, null=True, blank=True)      # name of attachment
    value = models.CharField(max_length=500, null=True, blank=True)
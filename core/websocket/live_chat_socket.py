import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import base64
import re
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import django
django.setup()
from sop_chat_service.app_connect.models import Attachment, Message, Room

class ChatConsumer(AsyncWebsocketConsumer):
    def base64_decode(data, name):
        '''decode the base64 string and create a compatible 
       file that Django recognize
    '''
        format, imgstr = data.split(';base64,') 
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=name + '.' + ext)
        return data

    def new_message(self, data):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        room = Room.objects.filter(room_id=self.room_id).first()
        message = Message.objects.create(text=data,room_id = room)
    def new_message_attachment(self, data):
        print("asdkaksjksk")
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        room = Room.objects.filter(room_id=self.room_id).first()
        message = Message.objects.create(room_id = room)

        format, imgstr = data.split(';base64,') 
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name="file" + '.' + ext)
        Attachment.objects.create(file = image,mid= message)
     
    async def connect(self):
        print('connect')
        await self.accept()
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        self.room_group_name = f'{self.topic}_{self.room_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print("222222222")
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message",None)
        file = text_data_json.get("file",None)

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        self.room_group_name = f'{self.topic}_{self.room_id}'
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    "message": message
                }
            )
            self.new_message(message)

        elif file:
            print("1717171717")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    "file": file
                }
            )
            self.new_message_attachment(file)
        
    async def chat_message(self, event):
        print("111111111")
        message = event.get("message",None)
        file = event.get("file",None)
        if message:
            await self.send(text_data=json.dumps({
                'message': message,
            }))
        elif file:
            await self.send(text_data=json.dumps({
            'message': "file sending",
        }))
  

    async def disconnect(self, close_code):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        self.room_group_name = f'{self.topic}_{self.room_id}'
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"Exit {self.channel_name}")



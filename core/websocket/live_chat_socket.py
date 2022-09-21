import json
from channels.generic.websocket import AsyncWebsocketConsumer
import base64
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

    async def new_message(self, data):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        room = Room.objects.filter(room_id=self.room_id).first()
        message = Message.objects.create(text=data,room_id = room)
        message = {
            "text": message.text,
            "room_id": self.room_id,
            "created_at":message.created_at
        }
        return message
        
    async def new_message_attachment(self, data):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        room = Room.objects.filter(room_id=self.room_id).first()
        message = Message.objects.create(room_id = room)

        format, imgstr = data.split(';base64,') 
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name="file" + '.' + ext)
        Attachment.objects.create(file = image,mid= message)
    
        
     
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        self.room_group_name = f'{self.topic}_{self.room_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    async def receive(self, text_data):
        self.topic = self.scope['url_route']['kwargs']['topic']

        text_data_json = json.loads(text_data)
        if self.topic == 'mesage':
            message = text_data_json.get("message",None)
            file = text_data_json.get("file",None)

            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'{self.topic}_{self.room_id}'
            if message:
                check =await self.new_message(message)
                print(check)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        "message": message
                    }
                )

            elif file:
                message = self.new_message_attachment(file)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        "message": message
                    }
                )
                
        elif self.topic =='new-room':
            room= text_data_json.get("room",None)
   
            self.room_group_name = f'{self.topic}'
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_room',
                    "room":  room
                }
            )
        
    async def chat_message(self, event):
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
    async def chat_room(self, event):
        room = event.get("room",None)
        room_check = Room.objects.filter(id = room)
        room_data = {
            "name" : room_check.name,
            "external_id":room_check.external_id,
            "user_id":room_check.user_id,
            "status":room_check.status,
            "room_id":room_check.room_id
        }
        await self.send(text_data=json.dumps({
            'room': f'{room_data}',
        }))
      
  

    async def disconnect(self, close_code):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        self.room_group_name = f'{self.topic}_{self.room_id}'
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"Exit {self.channel_name}")



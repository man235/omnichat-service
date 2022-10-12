# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# import base64
# from django.core.files.base import ContentFile
# from django.conf import settings
# from nats.aio.client import Client as NATS
# import django
# django.setup()
# import logging
# logger = logging.getLogger(__name__)


# nats_client = NATS()

# class SaleChatConsumer(AsyncWebsocketConsumer):
#     async def subscribe_handler_new_message(self, msg):
#         print("checking --------------- websocket ")
#         # data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
#         logger.debug(f'data subscribe natsUrl ----------------- {msg.data.decode("utf-8")}')
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'new_message',     # call func chat_message handler
#                 'message': msg.data.decode("utf-8")
#             }
#         )
  
#     async def connect(self):
       
#         self.room_group_name = "livechat_saleman"
#         await nats_client.connect(
#             servers=[settings.NATS_URL]
#         )
#         topics = [f'livechat.room.*',f'livechat.action.room.*']
        
#         sub=[]
#         for topic in topics:
#             if topic == topics[0]:
#                 sub = await nats_client.subscribe(topic, "saleman_message", self.subscribe_handler_new_message)
#             if topic == topics[1]:
#                 sub = await nats_client.subscribe(topic, "saleman_action_room", self.subscribe_handler_new_message)
#         self.sub = sub
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.sub.unsubscribe()
#         await nats_client.close()

#     async def receive(self, text_data):
#         logger.debug(f'receive data websocket ----------------- ===============')
#         pass

#     async def new_message(self, event):
#         message = event['message']
        
#         # message.events = "new_message"
#         await self.send(message)
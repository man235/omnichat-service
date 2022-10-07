from abc import ABC
from dataclasses import dataclass
from email.mime import image
import json
from typing import Any, BinaryIO, ClassVar, Optional, Protocol, TypeVar, Union
from django.conf import settings
import requests


#------------------- COMMON DATA ------------------------------------
@dataclass
class ZaloMessageDestination:
    access_token: str
    recipient_id: str
    sender_id: str = None
    message: dict = None
    url: str = f"{settings.ZALO_OA_OPEN_API}/message"
    content_type: str = "application/json"
    
    
@dataclass
class ZaloUploadDestination:
    access_token: str
    file: bytes
    _type_tuple: ClassVar[tuple] = ("file", "image", "gif")
    type: str in _type_tuple
    url: str = f"{settings.ZALO_OA_OPEN_API}/upload/{type}"
    content_type: str = "multipart/form-data"
    
    
#------------------- CHAT INTERFACE ------------------------------------
class MessageSender(ABC):    
    
    def send(self, message_formatter: ZaloMessageDestination) -> None:
        pass
    
    
class UploadSender(ABC):    
    
    def upload(self, upload_formatter: ZaloUploadDestination) -> None:
        pass
            
            
#------------------- SENDING CONTEXT ------------------------------------
class MessageSendingContext:
    
    def __init__(self, strategy: MessageSender) -> None:
        self._strategy = strategy
    
    @property
    def strategy(self) -> MessageSender:
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: MessageSender) -> None:
        self._strategy = strategy
    
    def call_chat_sender(self, message_formatter: ZaloMessageDestination) -> Any:
        if isinstance(self._strategy, MessageSender):
            return self._strategy.send(message_formatter)
        else:
            return None
    
    def call_upload_sender(self, upload_formatter: ZaloUploadDestination) -> Any:
        if isinstance(self._strategy, UploadSender):
            return self._strategy.upload(upload_formatter)
        else:
            return None
    
    
#------------------- SENDING IMPLEMENTATION ------------------------------------
class ZaloTextChatSender(MessageSender):
    
    def __init__(self):
        pass
    
    def send(self, message_formatter: ZaloMessageDestination) -> None:
        rp = requests.post(
            url = message_formatter.url,
            headers = {
                "Content-Type": message_formatter.content_type,
                "access_token": message_formatter.access_token,    
            },
            data = json.dumps({
                "recipient": {
                    "user_id": message_formatter.recipient_id,
                },
                "message": message_formatter.message,
            })
        )
        
        if rp.status_code == 200:
            rp_json = rp.json()
            
            return rp_json
        else:
            return None # BAD Request
        
        
class ZaloFileChatSender(MessageSender):
    def __init__(self):
        pass
    
    def send(self, message_formatter: ZaloMessageDestination) -> None:
        pass
    
    
class ZaloStickerChatSender(MessageSender):
    def __init__(self):
        pass
    
    def send(self, message_formatter: ZaloMessageDestination) -> None:
        pass
    
    
class ZaloImageChatSender(MessageSender):
    
    def __init__(self):
        pass
    
    def send(self, message_formatter: ZaloMessageDestination) -> None:
        
        pass
    
    
#------------------- UPLOAD IMPLEMENTATION ------------------------------------
class ZaloFileUploadSender(UploadSender):
    _type_upload = "file"
    
    def __init__():
        pass
    
    def upload(self, upload_formatter: ZaloUploadDestination) -> None:
        upload_formatter.type = self._type_upload
        pass
    

class ZaloImageUploadSender(UploadSender):
    _type_upload = "image"
    
    def __init__():
        pass
    
    def upload(self, upload_formatter: ZaloUploadDestination) -> None:
        upload_formatter.type = self._type_upload
        rp = requests.post(
            url = upload_formatter.url,
            headers = {
                "access_token": upload_formatter.access_token,    
            },
            files= upload_formatter.file,
        )
        
        if rp.status_code == 200:
            rp_json = rp.json()
            
            return rp_json
        else:
            return None # BAD Request
    

class ZaloGifUploadSender(UploadSender):
    
    def __init__():
        pass
    
    def upload(self, upload_formatter: ZaloUploadDestination) -> None:
        
        pass
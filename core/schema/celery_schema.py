# -*- coding: utf-8 -*-
from typing import List, Optional, Dict
from .base_model import CustomBaseModel

class ReminderSchema(CustomBaseModel):
    room_id: str
    user_id: str
    unit: Optional[str]
    title: Optional[str]
    time_reminder: Optional[int]
    repeat_time: Optional[int]
    created_at: Optional[str]
    is_active_reminder: Optional[bool]
    event: Optional[str]

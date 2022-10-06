# -*- coding: utf-8 -*-
from pydantic import BaseModel
import ujson


class CustomBaseModel(BaseModel):

    class Config:
        json_loads = ujson.loads
        json_dumps = ujson.dumps
        fields = {
            'from_': 'from'
        }

    def dict(self, *args, **kwargs):
        kwargs.update({'by_alias': True})
        return super().dict(*args, **kwargs)
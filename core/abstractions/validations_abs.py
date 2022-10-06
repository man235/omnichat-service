# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class AbsValidator(ABC):
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.private_name):
            if hasattr(self, 'default'):
                return getattr(self, 'default')
            return None
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value):
        pass

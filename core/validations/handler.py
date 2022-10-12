from core.abstractions import (
    AbsHandler,
    AbsValidator
)

# ------------------ Dict data with value is abstraction
class DictHandleValidator(AbsValidator):
    def __init__(self) -> None:
        self.default = None

    def validate(self, value):
        if not isinstance(value, dict):
            raise TypeError(f'Expected {value!r} to be an dict of type: handler_instance')
        for v in value.values():
            if not isinstance(v, AbsHandler):
                raise TypeError(f'Expected {v!r} to be an instance of AbsHandler')

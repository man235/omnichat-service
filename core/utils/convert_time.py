from core import constants

def convert_unit_time(unit_time, time):
    _time = 0
    if unit_time == constants.DAY:
        _time = time * 60 * 60 * 24
    elif unit_time == constants.HOUR:
        _time = time * 60 * 60
    elif unit_time == constants.MINUTE:
        _time = time * 60
    elif unit_time == constants.SECOND:
        _time = time
    return _time

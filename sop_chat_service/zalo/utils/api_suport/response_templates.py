from typing import Any
from unittest import result
from rest_framework.response import Response
from rest_framework import status


def json_response(is_success: bool, result: Any) -> Any:
    if is_success:
        return {
            'message': 'Success',
            'data': result
        }
    else:
        return {
            'message': 'Failure',
            'error': result,
        }

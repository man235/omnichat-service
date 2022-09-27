from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError



class Pagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'data': data
        }, status=status.HTTP_200_OK)
def file_size(value): # add this to some file where you can import it from
        limit = 5 * 1024 * 1024
        if value.size > limit:
            raise ValidationError('File too large. Size should not exceed 5 MB.')
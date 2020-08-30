from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class CredyMoviesPagination:

    def __init__(self):
        self.page_size = 10
        self.next_page = None
        self.prev_page = None
        self.count = None
        self.base_url = settings.LOCAL_URL

    def get_next_link(self):
        return self.base_url + '?page='+str(self.next_page) \
            if self.next_page else self.next_page

    def get_previous_link(self):
        if self.prev_page:
            if self.prev_page != 1:
                return self.base_url + '?page='+str(self.prev_page)
            return self.base_url
        return None

    def get_paginated_response(self, data):

        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        }, status=status.HTTP_200_OK)

    def paginate_queryset(self, queryset, page):
        start = (page-1)*self.page_size
        end = page*self.page_size
        self.count = queryset.count()
        self.prev_page = page if page != 1 else None
        self.next_page = page+1 if self.count > page*self.page_size \
            else None

        if self.count >= page*self.page_size:
            return queryset[start:end]
        return queryset[start:]

from .tasks import increase_counter
from django.utils.deprecation import MiddlewareMixin


class CountRequestMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if not request.path == '/request_count/reset/':
            increase_counter()
        return response

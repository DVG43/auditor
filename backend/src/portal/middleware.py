from settings import ALLOWED_HOSTS


class GetDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        pass

from django.contrib.auth import get_user_model

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_anonymous and request.META.get('REMOTE_ADDR') == '127.0.0.1':
            User = get_user_model()
            user = User.objects.filter(username='vallka').first()
            if user:
                request.user = user
                request.user.backend = 'django.contrib.auth.backends.ModelBackend'
        response = self.get_response(request)
        return response
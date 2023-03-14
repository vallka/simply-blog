from django.contrib import messages
from jinja2 import Environment
from django.conf import settings
from django.urls import reverse

class JinjaEnvironment(Environment):

    def __init__(self,**kwargs):
        super(JinjaEnvironment, self).__init__(**kwargs)
        self.globals['messages'] = messages.get_messages
        self.globals['settings'] = settings
        self.globals['url'] = reverse

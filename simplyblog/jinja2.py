from django.contrib import messages
from jinja2 import Environment
from django.conf import settings

class JinjaEnvironment(Environment):

    def __init__(self,**kwargs):
        super(JinjaEnvironment, self).__init__(**kwargs)
        self.globals['messages'] = messages.get_messages
        self.globals['settings'] = settings

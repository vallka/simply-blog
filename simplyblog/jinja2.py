from django.contrib import messages
from jinja2 import Environment

class JinjaEnvironment(Environment):

    def __init__(self,**kwargs):
        super(JinjaEnvironment, self).__init__(**kwargs)
        self.globals['messages'] = messages.get_messages

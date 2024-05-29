import json
from django.views import generic



# Create your views here.
class WeatherView(generic.TemplateView):
    template_name = 'weather/page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open('weather/good_forecast.json') as json_file:
            context['good_forecast'] = json.load(json_file) 

        return context 
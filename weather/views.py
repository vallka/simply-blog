from django.views import generic



# Create your views here.
class WeatherView(generic.TemplateView):
    template_name = 'weather/page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context 
from django.views import generic

from castles.models import Castle


# Create your views here.
class MapView(generic.TemplateView):
    template_name = 'castles/map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['castles'] = Castle.objects.all()
        

        return context 
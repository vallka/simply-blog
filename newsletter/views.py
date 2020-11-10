from django.shortcuts import redirect

# Create your views here.

def my_image(request):
    return redirect('/static/images/pixel.png')
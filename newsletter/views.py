from django.shortcuts import redirect

# Create your views here.

def my_image(request):
    return redirect('/static/images/pixel.png')

def click_redirect(request,uuid):
    path=request.GET['path']
    print ('click_redirect',uuid,path)

    return redirect('/' + path)

import os

def api_key(request):
    return {'api_key': os.environ.get('SCENEX_KEY')}
import os

from django.conf import settings
from django.shortcuts import render


# Create your views here.
def index(request):
    # we should change this PATH to STATIC_ROOT/inspector/visual-inspector once we do a serious deploy
    json_files_list = os.listdir(settings.JSON_INSPECTOR_FILES_ROOT)
    json_inspector_base_url = f'{settings.STATIC_URL}inspector/visual-inspector'
    return render(request, 'inspector/inspector-index.html',
                  {'json_files_list': json_files_list,
                   'base_url': json_inspector_base_url})

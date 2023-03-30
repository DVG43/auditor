import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django.template.loader import render_to_string
import settings

def my_view(request):
    as_file = request.GET.get('as_file')
    context = {'some_key': 'some_value'}
    #
    as_file =True
    aaa = os.path.join(settings.BASE_DIR, 'share/auditor-v2_statics/your-template-static.html')
    if as_file:
        content = render_to_string('poll/poll_index.html', context)
        with open(aaa, mode='w', encoding="utf-8") as static_file: #'xxxx/your-template-static.html'
            static_file.write(content)
            print('dddddddddd')
    context.update({'dev_path':'/statics/'})
    return render(request, 'poll/poll_index.html', context)

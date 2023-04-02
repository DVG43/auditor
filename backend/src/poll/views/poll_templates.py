import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django.template.loader import render_to_string
import settings
from poll.models import questions as questions_models



def my_view(request, pk):
    #as_file = request.GET.get('pk')
    context = {'some_key': 'some_value'}
    #
    as_file =True
    #instances = questions('856331c7-62d9-45e7-a0cf-ce09753d2e28')
    instances = questions_models.PageQuestion.objects.filter(poll_id=pk)
    context.update({'instances':instances})
    result_template_path = os.path.join(settings.MEDIA_ROOT, 'your-template-static.html')
    if as_file:
        content = render_to_string('poll/poll_index.html', context)
        with open(result_template_path, mode='w', encoding="utf-8") as static_file: #'xxxx/your-template-static.html'
            static_file.write(content)

    context.update({'dev_path':'/statics/'})
    return render(request, 'poll/poll_index.html', context)

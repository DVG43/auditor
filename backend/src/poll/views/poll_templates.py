import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
import settings
from poll.models import questions as questions_models
from poll.models import poll as poll_models
from django.core.files import File
from django.core.files.base import ContentFile


def template_view(request, templ_uuid):
    # as_file = request.GET.get('pk')
    context = {'some_key': 'some_value'}

    page_instances = questions_models.PageQuestion.objects.filter(poll__template_uuid=templ_uuid)
    if not page_instances:
        return redirect('templates_dont_exist')
    context.update({'instances': page_instances})

    context.update({'dev_path': '/statics/'})

    # # если надо сохранить шаблон в html файл, но небходимо добавить поле "poll_template" у модели Poll
    # content = render_to_string('poll/poll_index.html', context)
    # poll_instance = poll_models.Poll.objects.get(pk=pk)
    # name = "template_poll_"
    # poll_instance.poll_template.save(f'{name}{poll_instance.order_id}.html', ContentFile(content), save=True)

    return render(request, 'poll/poll_index.html', context)

def stopper_view(request):
    # as_file = request.GET.get('pk')

    return render(request, 'poll/stopper.html')

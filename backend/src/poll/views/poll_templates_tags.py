# создание пользовательских тэгов
from django import template
from poll.models import questions as questions_models

register = template.Library() #создаем экземпляр класса library через котор происходит регистрация собственных шаблонных тэгов

@register.simple_tag(name='getcats')          # декотратор для превращения функции в тэг
def get_categories(filter=None):
    if not filter:
        return questions_models.CheckQuestion.objects.all()
    else:
        return questions_models.CheckQuestion.objects.filter(parent_id=filter)

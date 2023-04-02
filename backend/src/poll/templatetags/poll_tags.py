# создание пользовательских тэгов
from django import template
from poll.models import questions as questions_models

register = template.Library() #создаем экземпляр класса library через котор происходит регистрация собственных шаблонных тэгов

def questions(page_id):
    ret = list()
    # превращаем в лист с помощью "list( ... .values())" для устранения ленивых запросов
    ret.extend(list(questions_models.TextQuestion.objects.filter(parent_id=page_id).values()))
    ret.extend(list(questions_models.NumberQuestion.objects.filter(parent_id=page_id).values()))
    ret.extend(list(questions_models.DateQuestion.objects.filter(parent_id=page_id).values()))
    ret.extend(list(questions_models.CheckQuestion.objects.filter(parent_id=page_id).values()))
    ret.extend(list(questions_models.YesNoQuestion.objects.filter(parent_id=page_id).values()))
    ret.extend(list(questions_models.ManyFromListQuestion.objects.filter(parent_id=page_id).values()))
    ret.extend(list(questions_models.SectionQuestion.objects.filter(parent_id=page_id).values()))

    return ret

@register.inclusion_tag(
    'poll/questions/recursive.html')  # тэг который возр-ет шаблон recursive.html с передачей в нее параметров "page_id"
def get_questions(page_id=None):
    instances = questions(page_id)
    return {"instances": instances}

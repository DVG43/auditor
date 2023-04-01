# создание пользовательских тэгов
from django import template
from poll.models import questions as questions_models

register = template.Library() #создаем экземпляр класса library через котор происходит регистрация собственных шаблонных тэгов

def questions(page_id):
    ret = list()

    ret.extend(questions_models.TextQuestion.objects.filter(parent_id=page_id))
    ret.extend(questions_models.NumberQuestion.objects.filter(parent_id=page_id))
    ret.extend(questions_models.DateQuestion.objects.filter(parent_id=page_id))
    ret.extend(questions_models.CheckQuestion.objects.filter(parent_id=page_id))
    ret.extend(questions_models.YesNoQuestion.objects.filter(parent_id=page_id))
    ret.extend(questions_models.ManyFromListQuestion.objects.filter(parent_id=page_id))
    ret.extend(questions_models.SectionQuestion.objects.filter(parent_id=page_id))

    return ret

@register.inclusion_tag(
    'poll/questions/recursive.html')  # тэг который возр-ет шаблон list_categories.html с передачей в нее параметров "cats"
def get_questions(page_id=None):

    instances = questions(page_id)

    return {"instances": instances}

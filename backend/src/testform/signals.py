from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from testform.models import TestFormQuestion
from testform.utils import QTYPE, EnumQuestion


@receiver(post_save, sender=TestFormQuestion)
def tf_question_save_handler(sender, **kwargs) -> None:
    """
    Сигнал доя создания и удаления конкретных типов вопросов
    """
    instance = kwargs['instance']
    q_type = instance.question_type
    if isinstance(q_type, EnumQuestion):
        q_type = q_type._value_
    elif q_type.count('.'):
        q_type = q_type.split('.')[-1]
    model = apps.get_model(app_label='testform', model_name=q_type)
    for i_type in (qtype[0] for qtype in QTYPE if qtype[0] != q_type):
        delmodel = apps.get_model(app_label='testform', model_name=i_type)
        delmodel.objects.filter(testform_question=instance).delete()
    q = model.objects.filter(testform_question=instance).first()
    if not q:
        new_q = model(testform_question=instance)
        new_q.save()



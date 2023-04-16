from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from testform.models import TestFormQuestion, TestForm, FinalTFQuestion
from testform.schema.utils import QTYPE


@receiver(post_save, sender=TestFormQuestion)
def tf_question_save_handler(sender, **kwargs) -> None:
    """
    Сигнал для регулирования количества типов вопросов для соответствующего TestFormQuestion.
    для инстанса TestFormQuestion можеть быть только один тип вопроса. В случае изменения типа вопроса,
    предыдущий удаляется.

    Также данный сигнал создает финальный вопрос при создании шаблона теста
    """
    instance = kwargs['instance']
    q_type = instance.question_type
    if q_type != 'FinalTFQuestion':
        model = apps.get_model(app_label='testform', model_name=q_type)
        for i_type in (qtype[0] for qtype in QTYPE if qtype[0] != q_type):
            delmodel = apps.get_model(app_label='testform', model_name=i_type)
            delmodel.objects.filter(testform_question=instance).delete()
        q = model.objects.filter(testform_question=instance).first()
        if not q:
            new_q = model(testform_question=instance)
            new_q.save()
    if kwargs["created"] and instance.question_type == 'FinalTFQuestion':
        FinalTFQuestion.objects.create(testform_question=instance,
                                       order_id=10000)


@receiver(post_save, sender=TestForm)
def testform_handler(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        TestFormQuestion.objects.create(testform=instance)
        TestFormQuestion.objects.create(testform=instance,
                                        question_type='FinalTFQuestion')



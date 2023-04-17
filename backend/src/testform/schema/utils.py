from enum import Enum

from django.db.models import Model, QuerySet
from django.utils.translation import gettext_lazy as _


QTYPE = [
    ("BaseTFQuestion", _("общий")),
    ("FinalTFQuestion", _("завершающий экран")),
]

ANSWER_TYPE = (
    ('text', 'text'),
    ('video', 'video'),
)

LOGO_CHOICE = (
    ("image", _("photo")),
    ("url", _("video")),
)

enum_fields = [
    'type_answer',
    'question_type',
]


class EnumQuestion(Enum):
    BaseQuestion = 'BaseTFQuestion'


class EnumTypeAnswer(Enum):
    Text = 'text'
    Video = 'video'


class EnumTypeLogo(Enum):
    Photo = 'image'
    URL = 'url'


def _normalize_enum_value(value: str | Enum) -> str:
    if isinstance(value, Enum):
        value = value._value_
    elif value.count('.'):
        value = str(value).split('.')[-1]
    return value


def update_attrs(instance: Model, data: dict) -> None:
    for k, v in data.items():
        if k in enum_fields:
            v = _normalize_enum_value(v)
        setattr(instance, k, v)
    instance.save()


def normalize_order(query_set: QuerySet) -> None:
    for i, v in enumerate(query_set, start=1):
        v.order_id = i
        v.save(update_fields=['order_id', ])


def get_question_logo_default():
    return list(dict(ANSWER_TYPE).keys())

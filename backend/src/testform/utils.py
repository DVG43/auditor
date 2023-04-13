from enum import Enum
from django.utils.translation import gettext_lazy as _


QTYPE = [
    ("BaseTFQuestion", _("общий")),
    ("FinalTFQuestion", _("завершающий экран")),
]


class EnumQuestion(Enum):
    BaseTFQuestion = 'BaseTFQuestion'
    FinalTFQuestion = 'FinalTFQuestion'


class EnumTypeAnswer(Enum):
    Text = 'text'
    Video = 'video'

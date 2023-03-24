
from .tasks.theme_to_text import generate as theme_to_text
from .tasks.text_rephrase import generate as text_rephrase
from .tasks.text_shorter import generate as text_shorter
from .tasks.text_continue import generate as text_continue
from .tasks.query_ai import generate as query_ai


def set_openai_api_key(api_key):
    """ Нет необходимости использовать, если ключ установлен через
        переменную окружения `OPENAI_API_KEY`.
    """
    import openai
    openai.api_key = api_key

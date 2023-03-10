
from .tasks.theme_to_text import generate as theme_to_text
from .tasks.rephrase import generate as rephrase


def set_openai_api_key(api_key):
    """ Нет необходимости использовать, если ключ установлен через
        переменную окружения `OPENAI_API_KEY`.
    """
    import openai
    openai.api_key = api_key

from .tasks.query_ai import generate as query_ai
from .tasks.standard_generation import generate as standard_generation

from .tasks.query_ai import generate_stream as query_ai_stream
from .tasks.standard_generation import generate_stream as standard_generation_stream


def set_openai_api_key(api_key):
    """ Нет необходимости использовать, если ключ установлен через
        переменную окружения `OPENAI_API_KEY`.
    """
    import openai
    openai.api_key = api_key


from ..engines import gpt_3_5_turbo_0301 as engine

ENGINE_CONFIG = {
    'max_tokens': 1500,

    # Set to `0` during development for determined answers from GPT
    'temperature': 0,
}

def get_prompt(text: str) -> str:
    """
    Сформировать промт для генерации сокращенной версии входного текста с
    сохранением смысла.

    Parameters
    ----------

    text : str
        Входной текст.


    Return
    ------
    str
        Строка-промт (prompt) для языковой модели.


    Example
    -------
    >>> get_prompt("<text to shorten>")
    Make this text less verbose:

    <text to shorten>
    """
    return (f'Make this text less verbose. The output must be in '
            f'the same language as the original text:\n\n{text.strip()}')


def generate(
        text: str,
        include_debug: bool = False,
    ) -> dict:
    """
    text:
    Искусственный интеллект - это область науки, которая занимается созданием компьютерных систем, способных выполнять задачи, которые ранее могли выполнять только люди. Сегодня искусственный интеллект используется в различных сферах, таких как медицина, финансы, производство и транспорт. Он позволяет автоматизировать процессы, улучшить качество продукции и услуг, а также повысить эффективность работы. Однако, с развитием искусственного интеллекта возникают и новые проблемы, такие как безработица и этические вопросы.

    Пример ответа gpt-3.5-turbo:
    Искусственный интеллект - наука, создающая компьютерные системы, которые могут выполнять задачи, ранее доступные только людям. Он применяется в медицине, финансах, производстве и транспорте, автоматизируя процессы, улучшая качество и повышая эффективность работы. Однако, его развитие вызывает новые проблемы, такие как безработица и этические вопросы.
    """

    prompt = get_prompt(text)

    response = engine.complete(prompt, config=ENGINE_CONFIG,
        include_debug=include_debug)

    return response



from ..engines import gpt_3_5_turbo_0301 as engine

# Целевое число слов для генерируемого текста
LEN_WORDS = 30

ENGINE_CONFIG = {
    'max_tokens': 1500,

    # Set to `0` during development for determined answers from GPT
    'temperature': 0,
}

def get_prompt(text: str, len_words: int) -> str:
    """
    Сформировать промт для генерации продолжения входного текста.

    Parameters
    ----------

    text : str
        Входной текст. Если последнее предложение не оканчивается точкой,
        то будет сгенерировано продолжение, иначе будет сгенерировано
        следующее предложение.

    len_words : int
        Примерная длина продолжения в словах. Языковая модель
        далеко не всегда идеально следует инстукциям, поэтому итоговая длина
        может варьироваться.


    Return
    ------
    str
        Строка-промт (prompt) для языковой модели.


    Example
    -------
    >>> get_prompt("<text to continue>", len_words=30)
    Continue the text. Use no more then 30 words:

    <text to continue>
    """
    if len_words < 1:
        raise ValueError(f'len_words expected to be >= 1, got: {len_words}')

    prompt = f'Continue the text. Use no more then {len_words} words:\n\n{text.strip()}'
    return prompt


def generate(
        text: str,
        include_debug: bool = False,
    ) -> dict:
    """
    text:
    Гиперкар - это автомобиль высшего класса, который обладает невероятной мощностью и скоростью, а также уникальным дизайном и технологиями.

    Пример ответа gpt-3.5-turbo:
    Он предназначен для настоящих автомобильных энтузиастов, которые готовы заплатить огромные деньги за эксклюзивность и неповторимость.
    """

    prompt = get_prompt(text, LEN_WORDS)

    response = engine.complete(prompt, config=ENGINE_CONFIG,
        include_debug=include_debug)

    return response


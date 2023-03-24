
from ..engines import chat_3_5_turbo_0301 as engine

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
        user_query: str,
        context: str = "",
        include_debug: bool = False,
    ) -> dict:
    """
    user_query: "напиши про собаку"
    context: None
    answer: '''
        Собака - это один из самых верных и преданных домашних питомцев.
        Они являются членами семьи и могут стать настоящим другом для своих
        хозяев. Собаки имеют разные породы, размеры и характеры, но все они
        нуждаются в заботе и внимании.
        ...
        '''

    user_query: "замени собаку на змею"
    context: 'Собака - это один из самых верных и преданных ...'
    answer: '''
        Змея - это один из самых необычных и экзотических домашних
        питомцев. Они могут быть очень красивыми и интересными, но требуют
        особого ухода и внимания. Змеи имеют разные виды, размеры и
        характеры, но все они нуждаются в заботе и правильном содержании.
        ...
        '''
    """
    if context:
        prompts = [context, user_query]
    else:
        prompts = user_query

    response = engine.complete(prompts, config=ENGINE_CONFIG,
        include_debug=include_debug)

    return response


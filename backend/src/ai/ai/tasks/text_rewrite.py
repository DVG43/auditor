
from ..engines import gpt_3_5_turbo_0301 as engine

ENGINE_CONFIG = {
    'max_tokens': 1500,

    # Set to `0` during development for determined answers from GPT
    'temperature': 0,
}


def get_prompt(text: str) -> str:
    """
    Сформировать промт для перефразирования текста.

    Parameters
    ----------

    text : str
        Входной текст, который требуется перефразировать, т.е.
        изложить другими словами.


    Return
    ------
    str
        Строка-промт (prompt) для языковой модели.


    Example
    -------
    >>> get_prompt("<text to rewrite>")
    Перефразируй:

    <text to rewrite>
    """

    prompt = f'Перефразируй:\n\n{text.strip()}'
    return prompt


def generate(
        text: str,
        include_debug: bool = False,
    ) -> dict:
    """
    How are you? → How are you doing?
    Ты как?      → Как твои дела?
    """

    prompt = get_prompt(text)

    response = engine.complete(prompt, config=ENGINE_CONFIG,
        include_debug=include_debug)

    return response


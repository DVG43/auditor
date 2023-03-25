import re

from ..engines import gpt_3_5_turbo_0301 as engine


ENGINE_CONFIG = {
    'max_tokens': 1500,

    # Set to `0` during development for determined answers from GPT
    'temperature': 0,
}


def get_prompt(text: str) -> str:
    """
    Промт для генерации нескольких вариантов одной фразы.

    >>> get_prompt("Пора менять карьеру и жизнь")
    'Six ways to say "Пора менять карьеру и жизнь" in the same language:'

    OpenAI example output:
        1. Пришло время менять профессию и жизнь.
        2. Настало время поменять профессию и жизнь.
        3. Пора изменить карьеру и жизнь.
        4. Пора сменить профессию и жизнь.
        5. Настало время принять решение об изменении карьеры и жизни.
        6. Настало время дл
    """
    return f'Six ways to say "{text.strip()}" in the same language:'


def postprocess_text(generated_text: str) -> list:
    """
    Удалить нумерацию.

    >>> print(postprocess_text('''\
    ...     1. Пришло время менять профессию и жизнь.
    ...     2. Настало время поменять профессию и жизнь.
    ...     3. Пора изменить карьеру и жизнь.
    ... '''))
    Пришло время менять профессию и жизнь.
    Настало время поменять профессию и жизнь.
    Пора изменить карьеру и жизнь.
    """
    r = re.compile('^\d+\.\s')

    lines = []
    for line in generated_text.strip().splitlines():
        new_line = r.sub('', line.strip())
        lines.append(new_line.strip())

    return lines


def generate(text: str, include_debug: bool = False) -> dict:
    prompt = get_prompt(text.replace('\r\n', ' ').replace('\n', ' '))

    response = engine.complete(prompt, config=ENGINE_CONFIG,
        include_debug=include_debug)

    if response['payload']:
        response['payload'] = postprocess_text(response['payload'])
    return response

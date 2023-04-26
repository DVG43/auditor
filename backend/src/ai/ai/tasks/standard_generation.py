from typing import Union, Generator

from . import query_ai


## Commands

# Commands settings
MAX_WORDS = 60

COMMANDS = {
    "Сократить текст": 'сократи текст',
    "Расширить текст": f'используй не более {MAX_WORDS} слов, добавь больше деталей',
    "Продолжить писать": f'используй не более {MAX_WORDS} слов, продолжи текст',
    "Изменить тон на обычный": 'измени тон текста на обычный',
    "Изменить тон на формальный": 'измени тон текста на формальный',
    "Подвести итог": 'подведи краткий итог',
    "Объяснить это": 'объясни это, кратко',
}

def generate(
    command: str,
    context: Union[str, None] = None,
    include_debug: bool = False,
) -> dict:

    if command not in COMMANDS:
        response = {
            'payload': None,
            'error': f'Unknown command "{command}"',
        }
    else:
        user_query = COMMANDS[command]
        response = query_ai.generate(user_query, context, include_debug)

    return response


def generate_stream(
    command: str,
    context: Union[str, None] = None,
    include_debug: bool = False,
) -> Generator:

    if command not in COMMANDS:
        raise ValueError(f'Command is not supported: "{command}"')

    user_query = COMMANDS[command]
    response = query_ai.generate_stream(user_query, context,
        include_debug)

    return response
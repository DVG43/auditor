
from ..engines import gpt_3_5_turbo_0301 as engine

# Целевое число слов для генерируемого текста
LEN_WORDS = 80

ENGINE_CONFIG = {
    'max_tokens': 1500,

    # Set to `0` during development for determined answers from GPT
    'temperature': 0,
}

def get_prompt(
        theme: str,
        len_words: int,
        tone: str = None,
        lang: str = None,
        keywords: str = None,
    ) -> str:
    """
    Сформировать промт для генерации абзаца с указанными
    параметрами.

    Parameters
    ----------

    theme : str
        Тема генерируемого текста.

    len_words : int
        Примерная длина результирующего текста в словах. Языковая модель
        далеко не всегда идеально следует инстукциям, поэтому итоговая длина
        может варьироваться.

    tone : str or None
        Тон текста. Некоторые варианты:
            grateful      # благодарный
            excited       # взволнованный
            rude          # грубый
            sad           # грустный
            informative   # информативный
            witty         # остроумный
            negative      # отрицательный
            neutral       # нейтральный
            positive      # положительный
            professional  # профессиональный
            convincing    # убедительный
            engaging      # увлекательный
            humorous      # юмористический

    lang : str or None
        Язык текста. Некоторые варианты: russian, english.
        По умолчанию `same as theme` - языковая модель получает
        задание на генерацию текста на том же языке, что и тема.

    keywords : str or None
        Список ключевых слов через запятую. Эти слова должны присутствовать
        в сгенерированном тексте.

    Return
    ------
    str
        Строка-промт (prompt) для языковой модели.


    Example
    -------

    >>> get_prompt("Искусственный интеллект")
    Write a paragraph of text given the following parameters.
    Theme: "Искусственный интеллект"
    Length: no more than 35 words
    Language: same as theme

    GPT-3 (text-davinci-003) example output:
        Искусственный интеллект (AI) - это программная технология, которая позволяет компьютеру
        выполнять задачи, которые раньше требовали от человека целый комплекс навыков и знаний.
        AI используется для автоматизации повседневных задач.
    """
    if len_words < 1:
        raise ValueError(f'len_words expected to be >= 1, got: {len_words}')

    lines = ['Write a paragraph of text given the following parameters.']

    theme = theme.replace('"', '')  # remove double quotes
    lines.append(f'Theme: "{theme}"')

    len_words = int(len_words)
    lines.append(f'Length: no more than {len_words} words')

    if tone:
        lines.append(f'Tone: {tone}')

    lang = lang if lang else 'same as theme'
    lines.append(f'Language: {lang}')

    if keywords:
        lines.append(f'Use keywords: {keywords}')

    return '\n'.join(lines)


def generate(
        theme: str,
        tone: str = None,
        lang: str = None,
        keywords: str = None,
        include_debug: bool = False,
    ) -> dict:

    prompt = get_prompt(theme, LEN_WORDS, tone=tone,
        lang=lang, keywords=keywords)

    response = engine.complete(prompt, config=ENGINE_CONFIG,
        include_debug=include_debug)

    # Postprocess
    if response['payload']:
        response['payload'] = response['payload'].strip()

    return response


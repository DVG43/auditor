from .models import Document, Element
import openai
import re
import math


def organize_data_row_sort_arrays(instance):
    # чистка и сортировка массивов сортировки
    instance_data_row_attribute = None
    for attr in dir(instance):
        if attr.endswith('element') or attr == 'locations':
            instance_data_row_attribute = getattr(instance, attr)
    instance_data_row = list(instance_data_row_attribute.values('id'))
    instance_data_row_ids = [data_row['id'] for data_row in instance_data_row]
    if set(instance_data_row_ids) != set(instance.data_row_order):
        diff = list(set(instance_data_row_ids)
                    .difference(set(instance.data_row_order)))
        instance.data_row_order += diff

    if instance.data_row_order:
        for idx in reversed(instance.data_row_order):
            if idx not in instance_data_row_ids:
                instance.data_row_order.remove(idx)
    else:
        for ident in instance_data_row_ids:
            instance.data_row_order.append(ident)

    # отключаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = False

    instance.save()

    # включаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = True

    return instance

def text_generator(prompt, model, max_tokens):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response


class AiTranslator:
    """
    Usage:

    prompt = AiTranslator.theme_to_paragraph_prompt(user_input)

    # generate text using OpenAI API

    result = AiTranslator.theme_to_paragraph_postprocess(ai_generated_text)
    """

    @staticmethod
    def estimate_num_tokens(string: str, surplus=100):
        """ Приблизительно оценить число токенов, без использования сторонних библиотек. """
        en_chars = sum(1 for c in string if ord(c) < 128)
        other_chars = len(string) - en_chars
        return math.ceil(en_chars * 0.25 + other_chars * 1.25) + surplus

    @staticmethod
    def theme_to_paragraph_prompt(
        theme: str,
        len_words: int = 35,
        tone: str = None,
        lang: str = None,
    ) -> str:
        """
        Промт для генерации абзаца указанной длины на заданную тему.

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


        Return
        ------
        str
            Строка-промт (prompt) для языковой модели.


        Example
        -------

        >>> AiTranslator.theme_to_paragraph_preprocess("Искусственный интеллект")
        Task: write a paragraph of text given following parameters
        Theme: "Искусственный интеллект"
        Length: 35 words
        Language: same as theme
        Result:

        GPT-3 (text-davinci-003) example output:
            Искусственный интеллект (AI) - это программная технология, которая позволяет компьютеру
            выполнять задачи, которые раньше требовали от человека целый комплекс навыков и знаний.
            AI используется для автоматизации повседневных задач.
        """
        if len_words < 1:
            raise ValueError(f'len_words expected to be >= 1, got: {len_words}')

        prompt = 'Task: write a paragraph of text given following parameters\n'

        theme = theme.replace('"', '')  # remove double quotes
        prompt += f'Theme: "{theme}"\n'

        len_words = int(len_words)
        prompt += f'Length: {len_words} words\n'

        if tone:
            prompt += f'Tone: {tone}\n'

        lang = 'same as theme' if lang is None else lang
        prompt += f'Language: {lang}\n'

        prompt += 'Result:'
        return prompt

    def theme_to_paragraph_postprocess(generated_text: str) -> str:
        ''' Удалить обрезанное предложение (текст после точки). '''
        return re.sub('(?<=\.)[^.]+$', '', generated_text.strip())

    @staticmethod
    def rephrase_prompt(text: str) -> str:
        """
        Промт для генерации нескольких вариантов одной фразы.

        >>> AiTranslator.rephrase_preprocess("Пора менять карьеру и жизнь")
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

    @staticmethod
    def rephrase_postprocess(generated_text: str) -> str:
        """
        Удалить нумерацию.

        >>> print(AiTranslator.rephrase_postprocess('''\
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


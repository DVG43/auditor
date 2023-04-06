
from ..engines import gpt_3_5_turbo_0301 as engine


ENGINE_CONFIG = {
    'max_tokens': 500,

    # Set to `0` during development for determined answers from GPT
    'temperature': 0.7,
}


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


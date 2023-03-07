from typing import Union

import openai


CONFIG_DEFAULT_CHAT = {
    # str : {'gpt-3.5-turbo', 'gpt-3.5-turbo-0301'}
    #     Chat models (2023-03-01).
    'model': 'gpt-3.5-turbo',

    # int or None : 0..4096
    #     Limit tokens generated (prompt is not included).
    #     None: max possible value given prompt length is used.
    'max_tokens': 16,

    # float : [0.0, 2.0]
    #     From fully determenistic output, to random output.
    'temperature': 0.7,

    # float : [0.0, 1.0]
    #     Fraction of the most probable next words to use.
    'top_p': 1.0,

    # bool : {False, True}
    #     Tokens will be sent as data-only server-sent events.
    #     Tutorial:
    #     - https://www.youtube.com/watch?v=x8uwwLNxqis
    #     - Stream Responses from OpenAI API with Python: A Step-by-Step Guide
    #     - Using `requests` and `sseclient`
    'stream': False,

    # str, array or None : None
    #     Stop sequence. Example:
    #     - prompt='Count to ten in english words.', stop=' three', response="\n\nOne, two,":
    #     - prompt='Count to ten in english words.', stop='three', response="\n\nOne, two, three"
    #     - prompt='Count to ten in english words.', stop='ee', response="\n\nOne, two, three"
    #     Details:
    #     - Last token will be ommitted only if fully matched.
    #     - Empty string ('') is equal to None.
    #     Bugs:
    #     - New line character (one or more '\n') gives error.
    #     - Empty array ([]) gives error.
    #     ?: does support integer token ids?
    'stop': None,

    # float : [-2.0, 2.0]
    #     Increase the model's likelihood to talk about new topics.
    'presence_penalty': 0.0,

    # float : [-2.0, 2.0]
    #     Decrease the model's likelihood to use the same words multiple times.
    'frequency_penalty': 0.0,

    # dict: {token_id: -100.0..100.0}
    #     Increase or decrease the probability of given tokens.
    #     Can't be None.
    'logit_bias': {},
}

CHAT_ROLE_SYSTEM = 'system'
CHAT_ROLE_USER = 'user'
CHAT_ROLE_ASSISTANT = 'assistant'


def openai_error_to_dict(e: Union[Exception, None]) -> dict:
    """
    Example output:
    {
      "error_type": "APIError",
      "message": "The server had an error processing ...",
      "http_status": 500,
      "headers": {
        "Date": "Fri, 03 Mar 2023 14:38:35 GMT",
        "Content-Type": "application/json",
        "Content-Length": "366",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Openai-Model": "gpt-3.5-turbo-0301",
        "Openai-Organization": "user-f1a4wvw7acmsrqqulryvdgzs",
        "Openai-Processing-Ms": "231",
        "Openai-Version": "2020-10-01",
        "Strict-Transport-Security": "max-age=15724800; includeSubDomains",
        "X-Request-Id": "5e42bc2c0f8244f10fd16064e447af7b"
      },
      "json_body": {
        "error": {
          "message": "The server had an error processing your request. ...",
          "type": "server_error",
          "param": null,
          "code": null
        }
      }
    }
    """
    if e is None:
        return None

    error_details = {
        'exception_type': type(e).__name__,
    }
    if e.args:
        error_details['message'] = e.args[0]
    if hasattr(e, 'http_status'):
        error_details['http_status'] = e.http_status
    if hasattr(e, 'headers'):
        error_details['headers'] = dict(e.headers)
    if hasattr(e, 'json_body'):
        error_details['json_body'] = e.json_body
    return error_details


def complete(
        user_prompt: str,
        system_prompt: str = None,
        config: dict = {},
        include_debug: bool = False,
    ) -> dict:
    '''
    >>> complete('Good day!', config=TaskChatConfig.THEME_TO_TEXT,
    ...     include_debug=True)
    {
      "payload": "Good day to you too! How may I assist you today?",
      "error": None,
      "debug_info": {
        "messages": [{"role": "user", "content": "Good day!"}],
        "config": {
          "model": "gpt-3.5-turbo",
          "max_tokens": 16, ...},
        "response": {
          "id": "chatcmpl-6qxOABZxYjQ9N0ELjkdqWkRKa7pdK",
          "object": "chat.completion",
          "created": 1678079366,
          "model": "gpt-3.5-turbo-0301",
          "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 15,
            "total_tokens": 25},
        "choices": [{
          "message": {
            "role": "assistant",
            "content": "Good day to you too! How may I assist you today?"},
          "finish_reason": "stop",
          "index": 0}],
      "response_ms": 582},
      "error_details": null}
    }

    >>> chat_completion('Good day!', include_debug=True)  # no API_KEY
    {'payload': None,
    'error': 'AI engine error',
    'debug_info': {
        'messages': ...,
        'config': {...},
        'response': None,
        'error_details': {
            'exception_type': 'AuthenticationError',
            'message': 'Incorrect API key provided ...',
            'http_status': 401,
            'headers': {
                'Date': 'Mon, 06 Mar 2023 05:22:16 GMT',
                'Content-Type': 'application/json; charset=utf-8',
                'Content-Length': '302',
                'Connection': 'keep-alive',
                'Vary': 'Origin',
                'X-Request-Id': '01b555ad6dbe70a28eebf07eeb0d1ac0',
                'Strict-Transport-Security': 'max-age=15724800; includeSubDomains'
            },
            'json_body': {
                'error': {
                    'message': 'Incorrect API key provided nnn',
                    'type': 'invalid_request_error',
                    'param': None,
                    'code': 'invalid_api_key'}}}}
    }
    '''
    def chat_role(role, content):
        return dict(role=role, content=content)

    config = {**CONFIG_DEFAULT_CHAT, **config}

    config_stop = config['stop']
    if type(config_stop) is str:
        if '\n' in config_stop and config_stop.strip('\n') == '':
            raise ValueError(
                f"`stop` can't contain newline characters only"
                f" (openai bug 2023-03-03), got: {config_stop!r}")
    else:
        if config_stop == [] or config_stop == ():
            raise ValueError(
                f"`stop` can't be an empty sequence"
                f" (openai bug 2023-03-03), got: {config_stop}")

    messages = []
    if system_prompt:
        messages.append(chat_role(CHAT_ROLE_SYSTEM, system_prompt))
    messages.append(chat_role(CHAT_ROLE_USER, user_prompt))

    payload = response = openai_error = None
    try:
        openai_response = openai.ChatCompletion.create(messages=messages, **config)
    except Exception as e:
        openai_error = e
    else:
        response = openai_response.to_dict_recursive()
        response['response_ms'] = openai_response.response_ms
        # May need to check for unexpected response, like `choices != []`
        payload = response['choices'][0]['message']['content']

    result = {
        'payload': payload,
        'error': 'AI engine error' if openai_error else None,
    }
    if include_debug:
        result.update({
            'debug_info': {
                'messages': messages,
                'config': config,
                'response': response,
                'error_details': openai_error_to_dict(openai_error),
            }
        })
    return result



# api

## First usage
Разработка на основе этого шаблона возможна как с разворачиванием окружения напрямую на машине так и с помощью docker.

Установка docker - [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

Установка docker-compose - [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

Для управления зависимостями используется [pipenv](https://pipenv.pypa.io/en/latest/).
Если [pipenv](https://pipenv.pypa.io/en/latest/) не установлен, установить:

- MacOS: `brew install pipenv`,

- Linux: `sudo pip install pipenv`,

- Windows: `pip install pipenv`

Затем 
- `pipenv install --dev` - Создание нового виртуального окружения и установка зависимостей для разработки.
- `pipenv run init` -   установка pre-commit скриптов.
## Запуск 

Запуск локально:

```bash
docker-compose up -d --build
```

### Структура проекта:

 - `/src` - рабочий каталог, содержит код сервера django и основной проект django 
   - `manage.py`  
 - `.editorconfig` - настройки ide, требует установки соответствующего плагина ([download page](https://editorconfig.org/#download))
 - `.env` - необходимо создать. **Должен присутствовать в .gitignore!** Содержит используемые для работы переменные ([об этом ниже](#переменные-окружения)).
   Доступ к переменным из кода получаем с помощью `os.enveron.get('var_name',default_value)`
 - `.gitatributes` - настройки поведения клиента git ([зачем это здесь?](https://htmlacademy.ru/blog/boost/tools/konec-stroki), [документация](https://git-scm.com/docs/gitattributes))
 - `.gitignore`
 - `gitlab-ci.yml` - настройки ci/cd
 - `.pre-commit-config.yml` - настройка pre-commit ([документация](https://pre-commit.com/))
 - `Docker-compose.yml` - конфигурация docker-compose для локального использования.
 - `Dockerfile` - конфигурация контейнера для локального использования.
 - `Docker-compose.dev.yml` - конфигурация docker-compose для использования на сервере разработки.
 - `Dockerfile.dev` - конфигурация контейнера для использования на сервере разработки.
 - `Pipfile` - настройки pipenv, описание зависимостей и тд(заменяет файл requirements.txt). 
 - `Pipenv.lock` - хранит версии используемых пакетов и их зависимостей
 - `pyproject.toml` - хранит настройки некотрых пакетов(pytest, coverage, commitizen)
 - `readme.md` - этот файл

### Переменные окружения
Также в корне проекта необходимо создать файл **.env** со следующими переменными:

Обязательно:
- `SECRET_KEY` - cекретный ключ Django
- `PYTHONPATH= ./src` - корень проекта
- `API_PG_DB` - название базы данных
- `API_PG_USER` - имя пользователя
- `API_PG_PASSWORD` - пароль
- `API_PG_HOST` - хост, для localhost: 127.0.0.1
- `API_PG_PORT` - порт по умолчанию: 5432

Пример содержимого файла **.env**:
  ```
  SECRET_KEY=+k*ppm$q7*z&1lc36u$mb4ttm_c32_gey5xbrhgq@f!9dfyfhygvh
  PYTHONPATH= ./src
  API_PG_DB=postgres
  API_PG_USER=postgres
  API_PG_PASSWORD=postgres
  API_PG_HOST=127.0.0.1
  API_PG_PORT=5432
  ```
## Использование

Для активации виртуального окружения используется команда 
- `pipenv shell` - Команда активирует виртуальное окружение и подгружает переменные из файла `.env` в корне проекта.

Рабочий процесс происходит приблизительно так:
- `pipenv shell` - активация окружения
- пишем код
- `pipenv run lint` - проверим code style
- `pipenv run fix` - если с code style все плохо, но можно поправить автоматически. Если не поможет, придется править в ручную.
- `pipenv run test` - по необходимости, проверим не поломалили тесты.
- `git status` покажет что наизменяли
- `git add` добовляет проверенные и протестированные изменения в коммит
- `cz commit` ([commitizen-tool](https://commitizen-tools.github.io/commitizen/)) фиксирует изменения(вместо git commit). **Сообщения коммитов пойдут в changelog.md!**
  Запускает pre-commit проверки
- Если pre-commit отработал нормально, отправляем в репо `git push`. Если нет - правим и заново начиная с `pipenv run lint`
- далее редактируем ...
  
Иногда возникает потребность выти из виртуального окружения. Для выхода из окружения можно использовать команду `exit`

Если нужно выполнить одну команду в виртуальном окружении c последующим выходом из него, возможно использовать
- `pipenv run < comands >`

Как пример: 
- `pipenv run lint` - выполнит команду `lint` содержащеюся в секции scripts в Pipenv файле.
    
Доступные команды:
- `pipenv run init` установка пре коммит хука.
- `pipenv run lint` проверка стиля написания кода ([flake8](https://flake8.pycqa.org/en/latest/), [rules](https://www.flake8rules.com/))
- `pipenv run fix` исправление стилистических ошибок - запустит [black](https://black.readthedocs.io/en/stable/)
- `pipenv run test` запуск связки [pytest](https://docs.pytest.org/en/stable/), [pytest-django](https://pytest-django.readthedocs.io/en/latest/) и [coverage](https://coverage.readthedocs.io/en/coverage-5.3/)
- `pipenv run serve` тоже что и `python ./src/manage.py runserver`, возможно не сработает на linux и MakOS

Кроме этого через `pipenv run` можно запустить любую другую команду и она выполнится в виртуальном окружении.

Если появятся вопросы: [@Aleksey_vi_Semenov](https://t.me/Aleksey_vi_Semenov)




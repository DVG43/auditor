# Django + DRF + djoser + simple_jwt

[djoser](https://djoser.readthedocs.io/en/latest/index.html)

[simple_jwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/index.html)

## Getting started

Для запуска сервисов с помощью docker compose нужна аунтефикация в gitlab container regisrtry:

```bash
docker login registry.gitlab.com -u gitlab+deploy-token-1390888 -p opPf7dsZVQkvzrQ7tuZo
```

Для управления зависимостями используется [pipenv](https://docs.pipenv.org/).

Для установки зависимостей локально:

```bash
pipenv sync
```

Для активации виртуального окружения:

```bash
pipenv shell
```


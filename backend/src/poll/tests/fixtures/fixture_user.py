import pytest

from user.models import User


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_superuser(email='admin@yamdb.fake', password='1234567')


@pytest.fixture
def create_user(django_user_model):
    def make_user(**kwargs):
        kwargs['password'] = '1234567'
        return django_user_model.objects.create(**kwargs)
    return make_user


@pytest.fixture
def get_user_client():
    def make_client(user):
        from rest_framework_jwt.settings import api_settings
        from rest_framework.test import APIClient

        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return client
    return make_client


@pytest.fixture
def token_admin(admin):
    from rest_framework_jwt.settings import api_settings
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    payload = jwt_payload_handler(admin)
    token = jwt_encode_handler(payload)
    return token


@pytest.fixture
def user_client(token_admin):
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'JWT {token_admin}')
    return client


@pytest.fixture
def create_user(django_user_model):
    def make_user(email):
        return django_user_model.objects.create_user(
            email=email,
            password='1234567'
        )
    return make_user


@pytest.fixture
def get_user_client():
    def make_client(user):
        from rest_framework.test import APIClient
        from rest_framework_jwt.settings import api_settings

        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return client
    return make_client

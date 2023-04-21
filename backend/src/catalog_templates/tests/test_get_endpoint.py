from django.test import TestCase

from accounts.models import User
from rest_framework.test import APIClient
from ..models import Template


class GetTemplateFilterTest(TestCase):
    fixtures = 'test_templates_with_user.json',

    POINT_URL = "http://127.0.0.1/api/v1/catalog_template/"
    USERMAIL = 'test@test.com'
    USERPASS = 'testpass'

    def setUp(self):
        self.client = APIClient()
        response = self.client.post(
            "http://localhost/api/v2/token/",
            {
                "email": self.USERMAIL,
                "password": self.USERPASS
            }
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_templates(self):
        response = self.client.get(self.POINT_URL)
        count = response.data['count']

        self.assertEqual(count, 3)

    def test_access_templates_not_own(self):
        second_user = User.objects.create_user(
            email='some@some.xzu',
            password='sometestpass'
        )
        template = Template.objects.last()
        template.owner = second_user
        template.save()

        response = self.client.get(self.POINT_URL)
        count = response.data['count']

        self.assertEqual(count, 2)

    def test_name_filter(self):
        response = self.client.get(self.POINT_URL)
        count = response.data['count']

        self.assertEqual(count, 3)
        response = self.client.get(self.POINT_URL, {'name': 'test'})
        self.assertEqual(response.data['count'], 1)

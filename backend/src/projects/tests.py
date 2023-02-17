from unittest import TestCase
from rest_framework.test import APIClient


class TestProject(TestCase):
    url = 'http://127.0.0.1:8000/api/v1/projects/'
    token = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjU5MzI4MjM5LCJpYXQiOjE2NTY3MzYyMzksImp0aSI6IjllYjBhOWM4MzllYTRlNTBiNmY3NTFiZjBlOThhYzhkIiwidXNlcl9pZCI6IjYwZmNiNjJlLTY3ZTMtNDYxNS1hNTYwLWNjMzkxNjE3ODMwZSJ9.rY4dfg7JS-a3rX5uSFdGU8qCuITFqhWsKG8DNqhWucM'


    def test_project_created(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            'name': 'Test project',
            'description': 'Test description'
        }
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['name'], response.data['name'])

        project_id = response.data['id']
        patch_data = {
            'name': 'Test name change',
            'description': 'Test description change'
        }
        url = self.url + str(project_id) + '/'
        response = client.patch(url, patch_data, format='json')
        self.assertEqual(patch_data['name'], response.data['name'])

        response = client.delete(url)
        self.assertEqual(response.status_code, 200)

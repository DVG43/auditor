from django.test import TestCase
from rest_framework.test import APIClient
from .models import Document
from accounts.models import User


class CreateTest(TestCase):
    API_URL = "http://127.0.0.1:8000/api/v1/"
    GRAPHQL_URL = f"{API_URL}graphql/"
    TOKEN_GET_URL = "http://localhost:8000/api/v2/token/"
    USERMAIL = 'test@somedomain.xyz'
    USERPASS = 'testpass#'

    def setUp(self):
        self.user = User.objects.create_user(
            email=self.USERMAIL,
            password=self.USERPASS
        )
        self.user.is_invited = True
        self.user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.TOKEN_GET_URL,
            {
                "email": self.USERMAIL,
                "password": self.USERPASS
            }
        )
        self.token = response.data['access']

    def test_shared_access_to_removed_nested_doc(self):
        def make_post_request(query_data):
            return self.client.post(self.GRAPHQL_URL, query_data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        # create folder
        response = self.client.post(
            'http://127.0.0.1:8000/api/v1/folders/',
            {"name": "Новая папка"},
            format='json')
        folder_id = response.data['id']
        # create document in folder
        query = 'mutation CreateDocument($folderId: ID!, $name: String!, $parent: ID) {\n  documentCreateDocument(\n    input: {folderId: $folderId, name: $name, parent: $parent}\n  ) {\n    ok\n    document {\n      id\n      name\n      content\n      docUuid\n      owner {\n        firstName\n        lastName\n        __typename\n      }\n      folder {\n        id\n        name\n        __typename\n      }\n      children {\n        id\n        name\n        __typename\n      }\n      lastModifiedUser\n      lastModifiedDate\n      documentLogo\n      perm\n      perms\n      orderId\n      dataRowOrder\n      docOrder\n      __typename\n    }\n    __typename\n  }\n}'
        query_data = {
            "operationName": "CreateDocument",
            "variables": {
                'folderId': int(folder_id),
                'name': "Документ"
            },
            "query": query
        }

        response = make_post_request(query_data)

        doc = response.json()['data']['documentCreateDocument']['document']
        doc_id = doc['id']
        doc_first_page_id = doc['children'][0]['id']
        # create nested pages
        query_data['variables']['parent'] = doc_first_page_id
        response = make_post_request(query_data)
        doc_nested_page_id = \
            response.json()['data']['documentCreateDocument']['document']['id']

        # sharing access to pages
        for page_id in doc_first_page_id, doc_nested_page_id:
            query_data = {
                "operationName": "OpenAccessDocument",
                "variables": {"id": page_id},
                "query": "mutation OpenAccessDocument($id: ID!) {\n  documentOpenAccessDocument(id: $id) {\n    ok\n    document {\n      docUuid\n      __typename\n    }\n    __typename\n  }\n}"
            }
            response = make_post_request(query_data)
            self.assertEqual(response.status_code, 200)


        # check public access to docs
        for page_id in doc_first_page_id, doc_nested_page_id:
            query_data = {
                "operationName": "GetDocument",
                "variables": {"docId": page_id},
                "query": "query GetDocument($docId: Int!) {\n  documentDocument(docId: $docId) {\n    id\n    name\n    content\n    docUuid\n    owner {\n      firstName\n      lastName\n      __typename\n    }\n    folder {\n      id\n      name\n      __typename\n    }\n    children {\n      id\n      name\n      __typename\n    }\n    lastModifiedUser\n    lastModifiedDate\n    documentLogo\n    perm\n    perms\n    orderId\n    dataRowOrder\n    docOrder\n    __typename\n  }\n}"
            }
            response = make_post_request(query_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json().get('errors'), None)
        # remove doc1
        query_data = {
            "operationName": "DeleteDocument",
            "variables": {"id": f"{doc_id}"},
            "query": "mutation DeleteDocument($id: Int!) {\n  documentDeleteDocument(id: $id) {\n    ok\n    id\n    __typename\n  }\n}"
        }
        response = make_post_request(query_data)
        self.assertEqual(response.json().get('errors'), None)

        # check public access to docs
        for page_id in doc_first_page_id, doc_nested_page_id:
            query_data = {
                "operationName": "GetDocument",
                "variables": {"docId": page_id},
                "query": "query GetDocument($docId: Int!) {\n  documentDocument(docId: $docId) {\n    id\n    name\n    content\n    docUuid\n    owner {\n      firstName\n      lastName\n      __typename\n    }\n    folder {\n      id\n      name\n      __typename\n    }\n    children {\n      id\n      name\n      __typename\n    }\n    lastModifiedUser\n    lastModifiedDate\n    documentLogo\n    perm\n    perms\n    orderId\n    dataRowOrder\n    docOrder\n    __typename\n  }\n}"
            }
            response = make_post_request(query_data)
            self.assertNotEqual(response.json().get('errors'), None)


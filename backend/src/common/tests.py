"""
Contains unit and integration tests for the app.
"""

import json
import os

from rest_framework import status
from rest_framework.test import APITestCase


class GetOpenGraphTagsViewTest(APITestCase):
    """Tests to check the processed urls from which meta tags OpenGraph are extracted."""

    @classmethod
    def setUpTestData(cls):
        os.environ['IS_TEST'] = 'True'
        cls.url = '/api/v1/url_opengraph/'
        cls.response_content = {
            'title': None,
            'description': None,
            'image': None,
        }

    def test_view_ok(self):
        """Checking the server response with the correct request.
        In case of test failure, check the test_url.
        """
        test_url = "https://www.sevastopol.kp.ru/online/news/5061298/"
        response = self.client.post(self.url, {'url': test_url}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_url_with_metatags(self):
        """Checking the correct receipt of meta tags for a URL with meta tags.
        In case of test failure, check the test_url."""

        test_url = "https://www.sevastopol.kp.ru/online/news/5061298/"
        response = self.client.post(self.url, {'url': test_url}, format='json')
        self.assertEqual(json.loads(response.content),
                         {
                             "title": "Севастопольский кот ежедневно встречает пассажиров "
                                      "на станции 1529 км в Инкермане",
                             "description": "Кот общается с людьми и поднимает им настроение.",
                             "image": "https://s13.stc.yc.kpcdn.net/share/i/12/12880293/"
                                      "cr-1200-630.wm-nspru-100-tl-0-0.t-10-5061298-ttps"
                                      "-54-14-32173D-990-l-85-m-1.t-10-5061298-ttps-54-"
                                      "14-FFF-990-l-85-m-1.t-4-1475127-asb"
                                      "-42-10-FFF-788-l-210-b-60.m2022-12-18T08-39-35.jpg"
                         }
                         )

    def test_view_url_without_metatags(self):
        """Checking the correct meta tags processing for a URL without meta tags.
        In case of test failure, check the test_url."""

        test_url = "https://vedmark.ru/?p=1752&ysclid=l8vjodowcz185410393"
        response = self.client.post(self.url, {'url': test_url}, format='json')
        self.assertEqual(json.loads(response.content), self.response_content)

    def test_view_wrong_url(self):
        """Checking the response processing for an incorrect URL."""

        test_url = "http://www.gogffgfole.com/"
        response = self.client.post(self.url, {'url': test_url}, format='json')
        self.assertEqual(json.loads(response.content), self.response_content)

    def test_view_wrong_url_format(self):
        """Checking the response processing if the URL format is incorrect."""

        test_url = "ewfiuwefiukhwe"
        response = self.client.post(self.url, {'url': test_url}, format='json')
        self.assertEqual(json.loads(response.content), self.response_content)

    def test_view_no_url(self):
        """Checking the response processing if the URL was not passed."""
        response = self.client.post(self.url, format='json')
        self.assertEqual(json.loads(response.content), self.response_content)

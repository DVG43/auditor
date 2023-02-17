import os
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase, APIClient
from accounts.models import User
from subscription.models import PaymentDetails, Tariff, TariffPeriod
from django.contrib.auth.hashers import make_password


class UserTests(APITestCase):
    def setUp(self):
        os.environ['IS_TEST'] = 'True'
        self.user = User.objects.create(email='exist@example.com', first_name='exist',
                                        is_verified=True, code='1234')
        self.user.set_password('exists')
        self.user.save()
        self.user2 = User.objects.create(email='exist2@example.com', first_name='exist',
                                         is_verified=False, code='1234')
        self.user2.set_password('exists')
        self.user2.save()

        pd = PaymentDetails.objects.create()
        trial_description = ' '
        trial = Tariff.objects.create(
            payment_details=pd,
            is_trial=True,
            tariff_name='',
            tariff_description=trial_description,
            base_month_price=0
        )
        TariffPeriod.objects.create(tariff=trial, month_amount='1')

    def test_create_user_success(self):
        url = reverse('accounts:signup_user')
        data = {'email': 'test@bk.ru', 'password': '12351759', 'first_name': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email='test@bk.ru').first_name, 'test')

    def test_create_user_wrong_data(self):
        url = reverse('accounts:signup_user')
        data = {'email': 'test@bk.ru', 'password': '12351759'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['first_name'],
                         [ErrorDetail(string='field required', code='required')])
        self.assertEqual(User.objects.filter(email='test@bk.ru').count(), 0)
        data = {'email': 'test@bk.ru', 'first_name': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'],
                         [ErrorDetail(string='field required', code='required')])
        data = {'email': 'test@bk.ru', 'password': '12345', 'first_name': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'],
                         [ErrorDetail(string='length must be 6 or more symbols', code='min_length')])

    def test_user_exist(self):
        url = reverse('accounts:signup_user')
        data = {'email': 'exist@example.com', 'password': 'exists', 'first_name': 'exist'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'address already exists')
        self.assertEqual(User.objects.filter(email='exist@example.com').count(), 1)

    def test_login_success(self):
        url = reverse('accounts:token_obtain_pair')
        data = {'email': 'exist@example.com', 'password': 'exists'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'exist@example.com')
        self.assertTrue(response.data['access'])

    def test_login_wrong_data(self):
        url = reverse('accounts:token_obtain_pair')
        data = {'email': 'wrong@example.com', 'password': 'exists'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['auth'], 'wrong credentials')
        data = {'email': 'exist@example.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['auth'], 'wrong credentials')
        data = {'email': 'exist@example.com', 'password': 'wrong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'],
                         [ErrorDetail(string='length must be 6 or more symbols', code='min_length')])

    # def test_email_verify(self):  # ЗАПУСКАТЬ ОТДЕЛЬНО ОТ ВСЕХ ТЕСТОВ, ИНАЧЕ ОШИБКА ПОСТГРЕС
    #     url = reverse('accounts:email_verify')
    #     data = {'email': 'exist2@example.com', 'password': 'exists', 'code': '1234'}
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(User.objects.get(email='exist2@example.com').is_verified, True)

    def test_email_verify_resend(self):
        url = reverse('accounts:email_verify_resend')
        data = {'email': 'exist2@example.com', 'password': 'exists'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(User.objects.get(email='exist2@example.com'), '1234')

    def test_email_change_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('accounts:email_change')
        data = {'new_email': 'new_exist@example.com'}
        response = client.post(url, data, format='json')
        code = User.objects.get(email='exist@example.com').code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(code, '1234')
        data = {'new_email': 'new_exist@example.com', 'code': code}
        url = reverse('accounts:email_change_confirm')
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(email='new_exist@example.com').count(), 1)
        self.assertEqual(User.objects.filter(email='exist@example.com').count(), 0)

    def test_email_change_failed(self):
        url = reverse('accounts:email_change')
        data = {'new_email': 'new_exist@example.com', 'email': 'exist@example.com', 'password': 'exists'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.get(email='exist2@example.com').code, '1234')
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('accounts:email_change')
        data = {'new_email': 'new_exist@example.com'}
        client.post(url, data, format='json')
        data = {'new_email': 'new_exist@example.com', 'code': '0000'}
        url = reverse('accounts:email_change_confirm')
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'],
                         ErrorDetail(string='wrong', code='invalid'))

    def test_change_password_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('accounts:change_password')
        data = {'old_password': 'exists', 'new_password': 'new_exists'}
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'password changed')

    def test_change_password_failed(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('accounts:change_password')
        data = {'old_password': 'exists', 'new_password': 'new'}
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'],
                         [ErrorDetail(string='minimum length 6 symbols', code='min_length')])
        data = {'old_password': 'exists', 'new_password': 'exists'}
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'],
                         [ErrorDetail(string='can not match old_password', code='invalid')])

    def test_recover_password_success(self):
        url = reverse('accounts:recover_password')
        data = {'email': 'exist@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'new password was sent')

    def test_recover_password_failed(self):
        url = reverse('accounts:recover_password')
        data = {'email': 'noname@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'],
                         ErrorDetail(string='not found', code='invalid'))

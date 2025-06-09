from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models.user import User
from rest_framework_simplejwt.tokens import RefreshToken


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.refresh_url = reverse('refresh')
        self.logout_url = reverse('logout')
        self.protected_url = reverse('protected-sample')

        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "strongpassword123",
            "password_confirm": "strongpassword123"
        }

    def register_user(self):
        return self.client.post(self.register_url, self.user_data, format='json')

    def login_user(self):
        login_data = {
            "identifier": self.user_data["email"],
            "password": self.user_data["password"]
        }
        return self.client.post(self.login_url, login_data, format='json')

    def test_register_success(self):
        response = self.register_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data['data'])

    def test_register_password_mismatch(self):
        data = self.user_data.copy()
        data['password_confirm'] = 'wrongpass'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        self.register_user()
        response = self.login_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data['data'])

    def test_login_invalid_password(self):
        self.register_user()
        response = self.client.post(self.login_url, {
            "identifier": self.user_data['email'],
            "password": "wrongpass"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_success(self):
        self.register_user()
        login_response = self.login_user()
        refresh_token = login_response.data['data']['tokens']['refresh']
        response = self.client.post(self.refresh_url, {"refresh_token": refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])

    def test_refresh_token_missing(self):
        response = self.client.post(self.refresh_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_route_with_token(self):
        self.register_user()
        login_response = self.login_user()
        access_token = login_response.data['data']['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_route_no_token(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        self.register_user()
        login_response = self.login_user()
        access_token = login_response.data['data']['tokens']['access']
        refresh_token = login_response.data['data']['tokens']['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.logout_url, {"refresh_token": refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_after_logout_should_fail(self):
        self.register_user()
        login_response = self.login_user()
        refresh_token = login_response.data['data']['tokens']['refresh']
        access_token = login_response.data['data']['tokens']['access']

        # Logout (blacklist refresh token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.post(self.logout_url, {"refresh_token": refresh_token}, format='json')

        # Attempt to refresh
        response = self.client.post(self.refresh_url, {"refresh_token": refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_after_logout_should_fail(self):
        self.register_user()
        login_response = self.login_user()
        refresh_token = login_response.data['data']['tokens']['refresh']
        access_token = login_response.data['data']['tokens']['access']

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.post(self.logout_url, {"refresh_token": refresh_token}, format='json')

        # Try accessing protected route
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



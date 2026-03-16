"""
Tests for authentication API endpoints.
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class AuthenticationAPITest(APITestCase):
    """
    Test suite for authentication endpoints.

    Tests registration, login, logout, and token refresh.
    """

    def setUp(self):
        """
        Set up test data.

        Creates test user for login/logout tests.
        """
        self.register_url = '/api/register/'
        self.login_url = '/api/login/'
        self.logout_url = '/api/logout/'
        self.refresh_url = '/api/token/refresh/'

        self.user_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'Test1234!',
            'confirmed_password': 'Test1234!'
        }

        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@test.com',
            password='Test1234!'
        )

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'User created successfully!')

        self.assertTrue(
            User.objects.filter(username='testuser').exists()
        )

    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = self.user_data.copy()
        data['confirmed_password'] = 'DifferentPassword!'

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username."""
        data = self.user_data.copy()
        data['username'] = 'existinguser'

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Test successful login with correct credentials."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'existinguser',
                'password': 'Test1234!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('user', response.data)

        self.assertEqual(response.data['user']['username'], 'existinguser')
        self.assertEqual(response.data['user']['email'], 'existing@test.com')

        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

        access_cookie = response.cookies['access_token']
        self.assertTrue(access_cookie['httponly'])

    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'existinguser',
                'password': 'WrongPassword!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_user_logout_success(self):
        """Test successful logout with token blacklist."""
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'existinguser',
                'password': 'Test1234!'
            },
            format='json'
        )

        access_token = login_response.cookies.get('access_token').value
        refresh_token = login_response.cookies.get('refresh_token').value

        self.client.cookies['access_token'] = access_token
        self.client.cookies['refresh_token'] = refresh_token

        logout_response = self.client.post(self.logout_url, format='json')

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', logout_response.data)

        self.assertEqual(logout_response.cookies['access_token'].value, '')
        self.assertEqual(logout_response.cookies['refresh_token'].value, '')

    def test_token_refresh_success(self):
        """Test successful token refresh."""
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'existinguser',
                'password': 'Test1234!'
            },
            format='json'
        )

        refresh_token = login_response.cookies.get('refresh_token').value

        self.client.cookies['refresh_token'] = refresh_token

        refresh_response = self.client.post(self.refresh_url, format='json')

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', refresh_response.data)

        self.assertIn('access_token', refresh_response.cookies)

    def test_token_refresh_missing_token(self):
        """Test token refresh fails without refresh token."""
        response = self.client.post(self.refresh_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

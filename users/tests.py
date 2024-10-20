from django.urls import reverse
from django.test import TestCase, Client
from rest_framework import status
from .models import User

class UserAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'password': 'securepassword'
        }
        self.user = User.objects.create(**self.user_data)

    def test_create_user_success(self):
        url = reverse('createUser')
        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'phone': '0987654321',
            'password': 'newpassword'
        }
        response = self.client.post(url, data, content_type='application/json')
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'User created successfully')
        self.assertIn('user_id', response_data)

    def test_create_user_missing_fields(self):
        url = reverse('createUser')
        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            # 'phone' and 'password' are missing
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_email_exists(self):
        url = reverse('createUser')
        data = {
            'name': 'Another User',
            'email': self.user.email,  # Existing email
            'phone': '1231231234',
            'password': 'anotherpassword'
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_success(self):
        url = reverse('getUser', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], self.user.name)

    def test_get_user_not_found(self):
        url = reverse('getUser', args=[999])  # Non-existing user ID
        response = self.client.get(url)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'User not found')

    def test_delete_user_success(self):
        url = reverse('deleteUser', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'User deleted')

    def test_delete_user_not_found(self):
        url = reverse('deleteUser', args=[999])  # Non-existing user ID
        response = self.client.delete(url)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'User not found')

    def tearDown(self):
        # Clean up after tests if necessary
        self.user.delete()
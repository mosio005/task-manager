from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationTests(TestCase):

    def setUp(self):
        User.objects.create_user(
            username='testuser',
            password='123456',
            email='test@example.com'
        )

    def test_jwt_authentication(self):
        client = APIClient()

        response = client.post(
            '/api/accounts/token/',
            {
                'username': 'testuser',
                'password': '123456'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)



    def test_jwt_authentication_unsuccessful(self):
        client = APIClient()

        response = client.post(
            '/api/accounts/token/',
            {
                'username': 'testuser',
                'password': '123457'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn('access', response.data)

    def test_login_nonexistent_user(self):
        client = APIClient()

        response = client.post(
            '/api/accounts/token/',
            {
                'username':'unknown_user',
                'password':'123456'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn('access', response.data)


    def test_register(self):
        client = APIClient()

        response = client.post(
            '/api/accounts/register/',
            {
                'username':'newuser',
                'email':'newuser@example.com',
                'password':'StrongPass123',
                'password_2':'StrongPass123',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(
                username='newuser'
            ).exists()
        )

        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password('StrongPass123'))
        self.assertNotEqual(user.password, 'StrongPass123')


    def test_register_duplicate_email(self):
        client = APIClient()

        response = client.post(
            '/api/accounts/register/',
            {
                'username':'newuser',
                'email':'test@example.com',
                'password':'StrongPass123',
                'password_2':'StrongPass123',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)


    def test_register_short_password(self):
        client = APIClient()

        response = client.post(
            '/api/accounts/register/',
            {
                'username': 'shortuser',
                'email': 'short@example.com',
                'password': '1234567',
                'password_2': '1234567',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(username='shortuser').exists()
        )

    def test_register_password_mismatch(self):
        client = APIClient()

        response = client.post(
            '/api/accounts/register/',
            {
                'username': 'mismatchuser',
                'email': 'mismatch@example.com',
                'password': 'StrongPass123',
                'password_2': 'DifferentPass123',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(username='mismatchuser').exists()
        )

    def test_register_duplicate_username(self):
        client = APIClient()
    
        response = client.post(
            '/api/accounts/register/',
            {
                'username': 'testuser',
                'email': 'another@example.com',
                'password': 'StrongPass123',
                'password_2': 'StrongPass123',
            },
            format='json'
        )
    
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            User.objects.filter(username='testuser').count(),
            1
        )
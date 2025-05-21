from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import CustomUser
from .serializers import UserRegistrationSerializer
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class CustomUserModelTests(TestCase):
    def test_create_user(self):
        """Test normal user creation with UUID"""
        user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='securepass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'User')
        self.assertFalse(user.is_superuser)
        self.assertIsInstance(user.user_id, uuid.UUID)
        
    def test_create_superuser(self):
        """Test superuser creation with admin role"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='adminpass123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, 'Admin')

class UserRegistrationSerializerTests(TestCase):
    def test_valid_registration(self):
        """Test valid user registration data"""
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'StrongPass123!'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_password(self):
        """Test weak password validation"""
        data = {
            'email': 'weakpass@example.com',
            'name': 'Weak User',
            'password': '123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_duplicate_email(self):
        """Test unique email validation"""
        User.objects.create_user(
            email='duplicate@example.com',
            name='Original User',
            password='testpass123'
        )
        data = {
            'email': 'duplicate@example.com',
            'name': 'Duplicate User',
            'password': 'AnotherPass123!'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class AuthViewTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'password': 'TestPass123!'
        }
        self.client = APIClient()

    def test_user_registration(self):
        """Test successful user registration"""
        url = reverse('user-signup')
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_registration(self):
        """Test registration with missing required fields"""
        url = reverse('user-signup')
        invalid_data = {'email': 'bad@example.com', 'password': 'testpass'}
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_authentication(self):
        """Test JWT token obtain and refresh flow"""
        User.objects.create_user(**self.user_data)
        
        # Test login
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Test token refresh
        refresh_url = reverse('refresh')
        response = self.client.post(refresh_url, {
            'refresh': response.data['refresh']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category

from travel.serializers import CategorySerializer


CATEGORY_URL = reverse('travel:category-list')


class PublicCategoryApiTests(TestCase):
    """Test the publicly available categories API"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_categories(self):
        """Test retrieving categories"""
        Category.objects.create(name='Museum')
        Category.objects.create(name='Pub')

        res = self.client.get(CATEGORY_URL)

        cats = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(cats, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category_failure(self):
        """Test that category creation not allowed to unauthenticated user"""
        payload = {'name': 'Sport'}
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTests(TestCase):
    """Test the authorized user category API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@anytestadressmail.com',
            'Test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_categories(self):
        """Test retrieving categories"""
        Category.objects.create(name='Museum')
        Category.objects.create(name='Pub')

        res = self.client.get(CATEGORY_URL)

        cats = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(cats, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category_successful(self):
        """Test creating a new category"""
        payload = {'name': 'test category'}
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Category.objects.filter(name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_category_invalid(self):
        """Test creating a new category with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_exists(self):
        """Test creating a category that already exists fails"""
        payload = {'name': 'Cafe'}
        Category.objects.create(name=payload['name'])
        res = self.client.post(CATEGORY_URL, payload)

        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)

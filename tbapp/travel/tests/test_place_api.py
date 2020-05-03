from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Place, Category

from travel.serializers import PlaceSerializer, PlaceDetailSerializer


PLACES_URL = reverse('travel:place-list')


def detail_url(place_id):
    """Return place detail URL"""
    return reverse('travel:place-detail', args=[place_id])


def sample_place(user, **params):
    """Create and return a sample place"""
    defaults = {
        'name': 'Anywhere buildings',
        'latitude': 30,
        'longitude': 60.5,
        'notes': 'I like here. Should be visited again!!',
        'external_source': 'www.anysourceblablablabla.com',
    }
    defaults.update(params)

    return Place.objects.create(user=user, **defaults)


def sample_category(name='Sapmle Category'):
    """Create and return a sample category"""
    return Category.objects.create(name=name)


class PublicPlaceApiTests(TestCase):
    """Test the publicly available place API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PLACES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlaceApiTests(TestCase):
    """Test authenticated place API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@anytestadressmail.com',
            'Test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_places(self):
        """Test retrieving places"""
        sample_place(user=self.user)
        sample_place(user=self.user)

        res = self.client.get(PLACES_URL)

        places = Place.objects.all().order_by('-id')
        serializer = PlaceSerializer(places, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_places_limited_to_user(self):
        """Test retrieving places for user"""
        user2 = get_user_model().objects.create_user(
            'other@anytestadressmail.com'
            'testpass'
        )
        sample_place(user=user2)
        sample_place(user=self.user)

        res = self.client.get(PLACES_URL)

        places = Place.objects.filter(user=self.user)
        serializer = PlaceSerializer(places, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_place_detail(self):
        """Test viewing a place detail"""
        place = sample_place(user=self.user)
        place.categories.add(sample_category())

        url = detail_url(place.id)
        res = self.client.get(url)

        serializer = PlaceDetailSerializer(place)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_place(self):
        """Test creating place"""
        payload = {
            'name': 'BJK Inonu Stadium',
            'latitude': 41,
            'longitude': 28,
            'notes': 'Football Temple',
            'external_source': 'https://www.openstreetmap.org/relation/6554433'
        }
        res = self.client.post(PLACES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        place = Place.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(place, key))

    def test_create_place_with_categories(self):
        """Test creating a place with categories"""
        category1 = sample_category(name='Stadium')
        category2 = sample_category(name='Sport')
        payload = {
            'name': 'BJK Inonu Stadium',
            'latitude': 41,
            'longitude': 28,
            'notes': 'Football Temple',
            'external_source': 'http://www.openstreetmap.org/relation/6554433',
            'categories': [category1.id, category2.id],
        }
        res = self.client.post(PLACES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        place = Place.objects.get(id=res.data['id'])
        cats = place.categories.all()
        self.assertEqual(cats.count(), 2)
        self.assertIn(category1, cats)
        self.assertIn(category2, cats)

    def test_partial_update_place(self):
        """Test updating a place with patch"""
        place = sample_place(user=self.user)
        place.categories.add(sample_category())
        new_cat = sample_category(name='City')

        payload = {'name': 'Istanbul', 'categories': [new_cat.id]}
        url = detail_url(place.id)
        self.client.patch(url, payload)

        place.refresh_from_db()
        self.assertEqual(place.name, payload['name'])
        cats = place.categories.all()
        self.assertEqual(len(cats), 1)
        self.assertIn(new_cat, cats)

    def test_full_update_place(self):
        """Test updating a place with put"""
        place = sample_place(user=self.user)
        place.categories.add(sample_category())
        payload = {
            'name': 'BJK Inonu Stadium',
            'latitude': 41,
            'longitude': 28,
            'notes': 'Football Temple',
            'external_source': 'http://www.openstreetmap.org/relation/6554433/'
        }
        url = detail_url(place.id)
        self.client.put(url, payload)

        place.refresh_from_db()
        self.assertEqual(place.name, payload['name'])
        self.assertEqual(place.latitude, payload['latitude'])
        self.assertEqual(place.longitude, payload['longitude'])
        self.assertEqual(place.notes, payload['notes'])
        self.assertEqual(place.external_source, payload['external_source'])

        cats = place.categories.all()
        self.assertEqual(len(cats), 0)

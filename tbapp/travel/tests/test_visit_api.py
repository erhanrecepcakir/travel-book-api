from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Visit, Place

from travel.serializers import VisitSerializer, VisitDetailSerializer


VISITS_URL = reverse('travel:visit-list')


def detail_url(visit_id):
    """Return visit detail URL"""
    return reverse('travel:visit-detail', args=[visit_id])


def sample_place(user, **params):
    """Create and return a sample place"""
    defaults = {
        'name': 'Anywhere buildings',
        'latitude': 30,
        'longitude': 60.5,
        'avg_score': 4.5,
        'notes': 'I like here. Should be visited again!!',
        'external_source': 'www.anysourceblablablabla.com',
    }
    defaults.update(params)

    return Place.objects.create(user=user, **defaults)


def sample_visit(user, **params):
    """Create and return a sample visit"""
    place = sample_place(user)
    defaults = {
        'title': 'Any Visit',
        'place': place,
        'score': 4.5,
        'notes': 'I like here.',
    }
    defaults.update(params)

    return Visit.objects.create(user=user, **defaults)


class PublicVisitApiTests(TestCase):
    """Test the publicly available visit API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(VISITS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVisitApiTests(TestCase):
    """Test authenticated visit API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@anytestadressmail.com',
            'Test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_visits(self):
        """Test retrieving visits"""
        sample_visit(user=self.user)
        sample_visit(user=self.user)

        res = self.client.get(VISITS_URL)

        visits = Visit.objects.all().order_by('-id')
        serializer = VisitSerializer(visits, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_visits_limited_to_user(self):
        """Test retrieving visits for user"""
        user2 = get_user_model().objects.create_user(
            'other@anytestadressmail.com'
            'testpass'
        )
        sample_visit(user=user2)
        sample_visit(user=self.user)

        res = self.client.get(VISITS_URL)

        visits = Visit.objects.filter(user=self.user)
        serializer = VisitSerializer(visits, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_visit_detail(self):
        """Test viewing a visit detail"""
        visit = sample_visit(user=self.user)

        url = detail_url(visit.id)
        res = self.client.get(url)

        serializer = VisitDetailSerializer(visit)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_visit(self):
        """Test creating visit"""
        place = sample_place(self.user)
        payload = {
            'title': 'Any Visit',
            'place': place.id,
            'score': 4.5,
            'notes': 'I like here.',
        }
        res = self.client.post(VISITS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        visit = Visit.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'place':
                self.assertEqual(place, visit.place)
            else:
                self.assertEqual(payload[key], getattr(visit, key))

    def test_partial_update_visit(self):
        """Test updating a visit with patch"""
        visit = sample_visit(user=self.user)
        new_place_payload = {
            'name': 'Taksim Square',
            'latitude': 30,
            'longitude': 60.5,
            'avg_score': 3,
            'notes': 'I like here. Should be visited again!!',
            'external_source': 'www.anysourceblablablabla.com',
        }
        new_place = sample_place(user=self.user, **new_place_payload)

        payload = {'title': 'Taksim Visiting', 'place': new_place.id}
        url = detail_url(visit.id)
        self.client.patch(url, payload)

        visit.refresh_from_db()
        self.assertEqual(visit.title, payload['title'])
        self.assertEqual(visit.place, new_place)

    def test_full_update_visit(self):
        """Test updating a visit with put"""
        visit = sample_visit(user=self.user)
        new_place_payload = {
            'name': 'Taksim Square',
            'latitude': 30,
            'longitude': 60.5,
            'avg_score': 3,
            'notes': 'I like here. Should be visited again!!',
            'external_source': 'www.anysourceblablablabla.com',
        }
        new_place = sample_place(user=self.user, **new_place_payload)
        payload = {
            'title': 'Taksim Square visit',
            'place': new_place.id,
            'score': 3,
            'notes': 'Different place!',
        }

        url = detail_url(visit.id)
        self.client.put(url, payload)

        visit.refresh_from_db()
        self.assertEqual(visit.title, payload['title'])
        self.assertEqual(visit.place, new_place)
        self.assertEqual(visit.score, payload['score'])
        self.assertEqual(visit.notes, payload['notes'])

    def test_filter_visits_by_places(self):
        """Test returning visits with specific place"""
        visit1 = sample_visit(user=self.user)
        visit2 = sample_visit(user=self.user)
        new_place_payload = {
            'name': 'Taksim Square',
            'latitude': 30,
            'longitude': 60.5,
            'avg_score': 3,
            'notes': 'I like here. Should be visited again!!',
            'external_source': 'www.anysourceblablablabla.com',
            }
        new_place = sample_place(user=self.user, **new_place_payload)
        visit1.place = new_place
        visit1.save()

        res = self.client.get(
            VISITS_URL,
            {'places': f'{new_place.id}'}
        )

        visit1 = VisitSerializer(visit1)
        visit2 = VisitSerializer(visit2)
        self.assertIn(visit1.data, res.data)
        self.assertNotIn(visit2.data, res.data)

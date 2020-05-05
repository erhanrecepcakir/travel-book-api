from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Plan, Visit, Place

from travel.serializers import PlanSerializer, PlanDetailSerializer


PLANS_URL = reverse('travel:plan-list')


def detail_url(plan_id):
    """Return plan detail URL"""
    return reverse('travel:plan-detail', args=[plan_id])


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


def sample_plan(user, **params):
    """Create and return a sample plan"""
    defaults = {
        'name': 'A Sample Travel Plan',
        'begins': '2020-01-01',
        'ends': '2020-01-05',
        'budget': 300,
        'done': True,
    }
    defaults.update(params)

    return Plan.objects.create(user=user, **defaults)


class PublicPlanApiTests(TestCase):
    """Test the publicly available plan API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PLANS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlanApiTests(TestCase):
    """Test authenticated plan API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@anytestadressmail.com',
            'Test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_plans(self):
        """Test retreiving plans"""
        sample_plan(user=self.user)
        sample_plan(user=self.user)

        res = self.client.get(PLANS_URL)

        plans = Plan.objects.all().order_by('-id')
        serializer = PlanSerializer(plans, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_plans_limited_to_user(self):
        """Test retrieving plans for user"""
        user2 = get_user_model().objects.create_user(
            'other@anytestadressmail.com',
            'testpass',
        )
        sample_plan(user=self.user)
        sample_plan(user=user2)

        res = self.client.get(PLANS_URL)

        plans = Plan.objects.filter(user=self.user)
        serializer = PlanSerializer(plans, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_plan_detail(self):
        """Test viewing a plan detail"""
        plan = sample_plan(user=self.user)

        url = detail_url(plan.id)
        res = self.client.get(url)

        serializer = PlanDetailSerializer(plan)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_plan(self):
        """Test creating plan"""
        payload = {
            'name': 'A Sample Travel Plan',
            'begins': '2020-01-01',
            'ends': '2020-01-05',
            'budget': 300,
            'done': True,
        }
        res = self.client.post(PLANS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        plan = Plan.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'begins' or key == 'ends':
                self.assertEqual(payload[key], str(getattr(plan, key)))
            else:
                self.assertEqual(payload[key], getattr(plan, key))

    def test_create_plan_with_visits(self):
        """Test creating a plan with visits"""
        visit1 = sample_visit(user=self.user)
        visit2 = sample_visit(user=self.user)

        payload = {
            'name': 'A Sample Travel Plan',
            'begins': '2020-01-01',
            'ends': '2020-01-05',
            'budget': 300,
            'done': True,
            'visits': [visit1.id, visit2.id],
        }
        res = self.client.post(PLANS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        plan = Plan.objects.get(id=res.data['id'])
        visits = plan.visits.all()
        self.assertEqual(visits.count(), 2)
        self.assertIn(visit1, visits)
        self.assertIn(visit2, visits)

    def test_partial_update_plan(self):
        """Test updating a plan with patch"""
        plan = sample_plan(user=self.user)
        plan.visits.add(sample_visit(user=self.user))
        new_visit = sample_visit(user=self.user)

        payload = {'name': 'New Plan Name', 'visits': [new_visit.id]}
        url = detail_url(plan.id)
        self.client.patch(url, payload)

        plan.refresh_from_db()
        self.assertEqual(plan.name, payload['name'])
        visits = plan.visits.all()
        self.assertEqual(len(visits), 1)
        self.assertIn(new_visit, visits)

    def test_full_update_plan(self):
        """Test updating a plan with put"""
        plan = sample_plan(user=self.user)
        plan.visits.add(sample_visit(user=self.user))
        payload = {
            'name': 'A new plan',
            'begins': '2020-05-01',
            'ends': '2020-05-08',
            'budget': 400,
            'done': False,
        }
        url = detail_url(plan.id)
        self.client.put(url, payload)

        plan.refresh_from_db()
        self.assertEqual(plan.name, payload['name'])
        self.assertEqual(str(plan.begins), payload['begins'])
        self.assertEqual(str(plan.ends), payload['ends'])
        self.assertEqual(plan.budget, payload['budget'])
        self.assertEqual(plan.done, payload['done'])

        visits = plan.visits.all()
        self.assertEqual(len(visits), 0)

    def test_filter_plans_by_visits(self):
        """Test returning plans with specific visits"""
        plan1 = sample_plan(user=self.user)
        plan2 = sample_plan(user=self.user)
        visit1 = sample_visit(user=self.user)
        visit2 = sample_visit(user=self.user)
        plan1.visits.add(visit1)
        plan2.visits.add(visit2)
        plan3 = sample_plan(user=self.user)

        res = self.client.get(
            PLANS_URL,
            {'visits': f'{visit1.id},{visit2.id}'}
        )

        serializer1 = PlanSerializer(plan1)
        serializer2 = PlanSerializer(plan2)
        serializer3 = PlanSerializer(plan3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
                                        IsAuthenticated

from core.models import Category, Place, Visit, Plan

from travel import serializers


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin):
    """Manage categories in the database"""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """Return objects"""
        return self.queryset.order_by('-name')


class PlaceViewSet(viewsets.ModelViewSet):
    """Manage places in the database"""
    serializer_class = serializers.PlaceSerializer
    queryset = Place.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the places for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.PlaceDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class VisitViewSet(viewsets.ModelViewSet):
    """Manage visits in the database"""
    serializer_class = serializers.VisitSerializer
    queryset = Visit.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the places for the authenticated user"""
        queryset = self.queryset
        places = self.request.query_params.get('places')
        if places:
            place_ids = self._params_to_ints(places)
            queryset = queryset.filter(place__id__in=place_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.VisitDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new visit"""
        serializer.save(user=self.request.user)


class PlanViewSet(viewsets.ModelViewSet):
    """Manage plans in the database"""
    serializer_class = serializers.PlanSerializer
    queryset = Plan.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Reetrieve the plans for the authenticated user"""
        queryset = self.queryset
        visits = self.request.query_params.get('visits')
        if visits:
            visits_ids = self._params_to_ints(visits)
            queryset = queryset.filter(visits__id__in=visits_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.PlanDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new plan"""
        serializer.save(user=self.request.user)

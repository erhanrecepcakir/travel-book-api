from rest_framework import serializers

from core.models import Category, Place, Visit


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category objects"""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)


class PlaceSerializer(serializers.ModelSerializer):
    """Serialize a place"""
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Place
        fields = (
            'id', 'name', 'latitude', 'longitude', 'categories', 'avg_score',
            'notes', 'external_source'
        )
        read_only_fields = ('id', 'avg_score')


class PlaceDetailSerializer(PlaceSerializer):
    """Serializer a place detail"""
    categories = CategorySerializer(many=True, read_only=True)


class VisitSerializer(serializers.ModelSerializer):
    """Serialize a visit"""
    place = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Place.objects.all()
    )

    class Meta:
        model = Visit
        fields = ('id', 'title', 'place', 'time', 'score', 'notes')
        read_only_fields = ('id',)


class VisitDetailSerializer(VisitSerializer):
    """Serializer a visit detail"""
    place = PlaceSerializer(many=False, read_only=True)

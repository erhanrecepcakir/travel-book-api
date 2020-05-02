from rest_framework import serializers

from core.models import Category, Place


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
            'id', 'name', 'latitude', 'longitude', 'categories', 'score',
            'notes', 'external_source'
        )


class PlaceDetailSerializer(PlaceSerializer):
    """Serializer a place detail"""
    categories = CategorySerializer(many=True, read_only=True)

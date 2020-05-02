from django.urls import path, include

from rest_framework.routers import DefaultRouter

from travel import views


router = DefaultRouter()
router.register('categorys', views.CategoryViewSet)
router.register('places', views.PlaceViewSet)


app_name = 'travel'

urlpatterns = [
    path('', include(router.urls))
]

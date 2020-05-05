from django.urls import path, include

from rest_framework.routers import DefaultRouter

from travel import views


router = DefaultRouter()
router.register('categorys', views.CategoryViewSet)
router.register('places', views.PlaceViewSet)
router.register('visits', views.VisitViewSet)
router.register('plans', views.PlanViewSet)


app_name = 'travel'

urlpatterns = [
    path('', include(router.urls))
]

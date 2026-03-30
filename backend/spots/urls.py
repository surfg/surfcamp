from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurfSpotViewSet

router = DefaultRouter()
router.register('spots', SurfSpotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

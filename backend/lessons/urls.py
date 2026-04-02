from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurfLessonViewSet, LessonProviderViewSet

router = DefaultRouter()
router.register(r'lessons', SurfLessonViewSet, basename='lesson')
router.register(r'providers', LessonProviderViewSet, basename='provider')

urlpatterns = [
    path('', include(router.urls)),
]

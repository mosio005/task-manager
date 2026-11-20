from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskCommentViewSet


router = DefaultRouter()

router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'comments', TaskCommentViewSet, basename='comments')


urlpatterns = [
    path('', include(router.urls)),
]
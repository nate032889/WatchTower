"""
URL configuration for watchtower project.
"""
from api.v1.prompt import PromptViewSet
from api.v1.metadata import APIMetadataViewSet
from api.v1.integrations import BotIntegrationViewSet
from api.v1.interactor import InteractorViewSet
from rest_framework.routers import SimpleRouter
from django.urls import path, include

router = SimpleRouter()
router.register(r'', APIMetadataViewSet, basename='api-v1-root')
router.register(r'prompt', PromptViewSet, basename='prompt')
router.register(r'bot-integrations', BotIntegrationViewSet, basename='bot-integrations')
router.register(r'interactor', InteractorViewSet, basename='interactor')

urlpatterns = [
    path(r'', include(router.urls)),
]

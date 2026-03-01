"""
URL configuration for watchtower project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from api.v1.prompt import PromptViewSet
from api.v1.metadata import APIMetadataViewSet
from rest_framework.routers import SimpleRouter
from django.contrib import admin
from django.urls import path, include

router = SimpleRouter()
router.register(r'', APIMetadataViewSet, basename='api-v1-root')
router.register(r'prompt', PromptViewSet, basename='prompt')

urlpatterns = [
    path(r'', include(router.urls)),
]

from rest_framework import viewsets, permissions
from api.models import BotIntegration
from api.serializers.integrations import BotIntegrationSyncSerializer

class BotIntegrationSyncViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only endpoint for internal services to sync bot state.
    This endpoint exposes the bot token and should only be accessible
    on the internal network.
    """
    queryset = BotIntegration.objects.filter(is_active=True)
    serializer_class = BotIntegrationSyncSerializer
    # In a real production environment, you would add IP-based permissions
    # to ensure only the fleet_manager can access this.
    # permission_classes = [IsInternalService]

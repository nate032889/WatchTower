from rest_framework import viewsets, permissions
from api.models import BotIntegration
from api.serializers.integrations import BotIntegrationSerializer

class BotIntegrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Bot Integrations to be viewed or edited.
    """
    queryset = BotIntegration.objects.all().order_by('-created_at')
    serializer_class = BotIntegrationSerializer
    # permission_classes = [permissions.IsAuthenticated] # Add this back for production

    def get_queryset(self):
        """
        This view should return a list of all the integrations
        for the currently authenticated user's organization.
        """
        # In a real app, you would filter by the user's organization
        # user = self.request.user
        # return BotIntegration.objects.filter(organization=user.organization)
        return BotIntegration.objects.all()

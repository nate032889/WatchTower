from rest_framework import viewsets
from api.models import ProviderCredential
from api.serializers.provider_credentials import ProviderCredentialSerializer

class ProviderCredentialViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing LLM Provider Credentials.
    """
    queryset = ProviderCredential.objects.all()
    serializer_class = ProviderCredentialSerializer

    def get_queryset(self):
        # In a real app, filter by the user's organization
        return ProviderCredential.objects.all()

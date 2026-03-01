from rest_framework import serializers
from api.models import ProviderCredential

class ProviderCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderCredential
        fields = ['id', 'organization', 'provider', 'api_key', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'api_key': {'write_only': True} # Never send the API key back to the client
        }

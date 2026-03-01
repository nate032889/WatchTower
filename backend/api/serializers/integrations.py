from rest_framework import serializers
from api.models import BotIntegration

class BotIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotIntegration
        fields = ['id', 'organization', 'platform', 'bot_token', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'bot_token': {'write_only': True} # Never send the token back to the client
        }

class BotIntegrationSyncSerializer(serializers.ModelSerializer):
    """
    A serializer for internal services that NEED to see the bot token.
    """
    class Meta:
        model = BotIntegration
        # Explicitly include the bot_token for the fleet manager's sync.
        fields = ['organization', 'platform', 'bot_token', 'is_active']

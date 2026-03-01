from rest_framework import serializers
from api.models import BotIntegration

class BotIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotIntegration
        fields = ['id', 'organization', 'platform', 'bot_token', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

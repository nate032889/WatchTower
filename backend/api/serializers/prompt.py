from rest_framework import serializers
from agents.types import LLMProvider

class HistoryItemSerializer(serializers.Serializer):
    """
    Serializer for a single item in the conversation history.
    """
    role = serializers.ChoiceField(choices=['user', 'model'])
    parts = serializers.ListField(child=serializers.CharField())

class MetadataSerializer(serializers.Serializer):
    """
    Serializer for the required metadata object.
    """
    domain = serializers.CharField(required=True, allow_blank=False)
    workflow = serializers.CharField(required=True, allow_blank=False)
    # Add other required metadata fields here in the future

class PromptSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, allow_blank=False) # Renamed from 'prompt'
    provider = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in LLMProvider],
        default=LLMProvider.GEMINI.value
    )
    history = HistoryItemSerializer(many=True, required=False)
    metadata = MetadataSerializer(required=True) # Enforce presence of metadata

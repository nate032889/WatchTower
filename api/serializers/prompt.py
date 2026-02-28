from rest_framework import serializers
from agents.types import LLMProvider

class HistoryItemSerializer(serializers.Serializer):
    """
    Serializer for a single item in the conversation history.
    This must match the structure expected by the Gemini SDK's ContentDict.
    """
    role = serializers.ChoiceField(choices=['user', 'model'])
    parts = serializers.ListField(child=serializers.CharField())

class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, allow_blank=False)
    provider = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in LLMProvider],
        default=LLMProvider.GEMINI.value
    )
    # The history is optional and can be a list of user/model interactions.
    history = HistoryItemSerializer(many=True, required=False)

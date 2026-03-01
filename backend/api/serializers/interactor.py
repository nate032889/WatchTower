from rest_framework import serializers

class IncomingMessageSerializer(serializers.Serializer):
    """
    Validates the incoming payload from a stateless bot interactor (e.g., Fleet Manager).
    """
    platform = serializers.CharField(required=True)
    channel_id = serializers.CharField(required=True)
    user_id = serializers.CharField(required=True)
    content = serializers.CharField(allow_blank=True)
    attachment_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=[]
    )

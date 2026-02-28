from rest_framework import viewsets
from rest_framework.response import Response

class APIMetadataViewSet(viewsets.ViewSet):
    """
    Metadata ViewSet to handle the API root.
    """

    def list(self, request):
        return Response({
            "name": "WatchTower API",
            "version": "v1",
            "status": "operational",
            "available_resources": {
                "prompts": request.build_absolute_uri('prompt/')
            }
        })
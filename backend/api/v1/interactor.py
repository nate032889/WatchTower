from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from api.serializers.interactor import IncomingMessageSerializer
from api.services.interactor_service import InteractorService

class InteractorViewSet(viewsets.ViewSet):
    """
    A thin ViewSet for receiving messages from stateless bot interactors.
    It strictly validates and passes data to the service layer.
    """
    
    @action(detail=False, methods=['post'], url_path='message')
    def message(self, request):
        """
        Receives a message payload, validates it, and passes it to the InteractorService.
        """
        # 1. Validate the incoming payload
        serializer = IncomingMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Pass validated data directly to the service layer
        # (This assumes InteractorService and its method exist)
        result = InteractorService.process_incoming_message(serializer.validated_data)

        # 3. Return the service layer's response
        if result.success:
            return Response({"response": result.data}, status=result.status_code)
        else:
            return Response({"error": result.error_message}, status=result.status_code)

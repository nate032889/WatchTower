import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from api.serializers.interactor import IncomingMessageSerializer
from api.services.interactor_service import InteractorService

logger = logging.getLogger(__name__)

class InteractorViewSet(viewsets.ViewSet):
    """
    A thin ViewSet for receiving messages from stateless bot interactors.
    It uses DRF Serializers for request validation.
    """
    
    @action(detail=False, methods=['post'], url_path='message')
    def message(self, request):
        """
        Receives a message payload, validates it, and passes it to the InteractorService.
        """
        serializer = IncomingMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data, err = InteractorService.process_incoming_message(serializer.validated_data)

        if err:
            logger.error(f"InteractorService failed to process message: {err}", exc_info=err)
            return Response(
                {"error": "An internal error occurred while processing the message."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({"response": data}, status=status.HTTP_200_OK)

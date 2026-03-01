from rest_framework import viewsets
from rest_framework.response import Response
from api.services.prompt_service import PromptService


class PromptViewSet(viewsets.ViewSet):
    """
    POST /v1/prompt/
    """

    def create(self, request):
        # Call the service layer to handle the request
        result = PromptService.process_prompt_request(request.data)

        # Use a guard clause to handle the failure case first.
        if not result.success:
            return Response({"error": result.error_message}, status=result.status_code)
        # If successful, return the data.
        return Response({"response": result.data}, status=result.status_code)

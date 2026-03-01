from agents.types import ServiceResult
from typing import Dict, Any

class IntakeValidationService:
    """
    A service to validate incoming data against our safety and schema standards.
    """

    # Mock controlled vocabulary for demonstration purposes
    ALLOWED_DOMAINS = {"security", "it_operations", "network"}
    ALLOWED_WORKFLOWS = {"ctf", "pentest", "incident_response"}

    @staticmethod
    def validate_vocabulary(metadata: Dict[str, Any]) -> ServiceResult:
        """
        Validates metadata against controlled vocabulary.
        Assumes schema/presence has already been validated by a serializer.

        :param metadata: The dictionary payload of metadata to validate.
        :return: A ServiceResult indicating success or failure with guidance.
        """
        # 1. Controlled Vocabulary Check: Domain
        domain = metadata.get("domain")
        if domain not in IntakeValidationService.ALLOWED_DOMAINS:
            return ServiceResult(
                success=False,
                status_code=400,
                error_message=f"Validation Failed: The domain '{domain}' is not valid. "
                              f"Allowed domains are: {', '.join(IntakeValidationService.ALLOWED_DOMAINS)}."
            )

        # 2. Controlled Vocabulary Check: Workflow
        workflow = metadata.get("workflow")
        if workflow not in IntakeValidationService.ALLOWED_WORKFLOWS:
            return ServiceResult(
                success=False,
                status_code=400,
                error_message=f"Validation Failed: The workflow '{workflow}' is not valid. "
                              f"Allowed workflows are: {', '.join(IntakeValidationService.ALLOWED_WORKFLOWS)}."
            )

        return ServiceResult(success=True, status_code=200)

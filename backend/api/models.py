from django.db import models
from django.contrib.auth.models import User
from agents.types import LLMProvider

# --- Multi-tenancy and Configuration Models ---

class Organization(models.Model):
    """Represents a tenant in the system."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Template(models.Model):
    """Represents a reusable system prompt template for an organization."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    system_prompt_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'name')

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

class ApiKey(models.Model):
    """API keys are now scoped to an Organization instead of a User."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=255, unique=True) # In a real app, this would be hashed
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Key for {self.organization.name}"

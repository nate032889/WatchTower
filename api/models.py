from django.db import models
from django.contrib.auth.models import User
from agents.types import LLMProvider

class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    provider = models.CharField(max_length=50, choices=[(tag.value, tag.name) for tag in LLMProvider])
    encrypted_key = models.CharField(max_length=255) # In a real app, this would be encrypted
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'provider')

    def __str__(self):
        return f"{self.user.username}'s {self.get_provider_display()} Key"

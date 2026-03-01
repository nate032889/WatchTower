from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from api.infrastructure.redis_publisher import publish_bot_command

# --- Core Multi-Tenant and Operational Models ---

class Organization(models.Model):
    """Represents a tenant in the system (e.g., a company or a team)."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class ApiKey(models.Model):
    """API keys are scoped to an Organization for multi-tenant authentication."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Key for {self.organization.name}"

class ProviderCredential(models.Model):
    """Stores third-party LLM provider credentials for an organization."""
    PROVIDER_CHOICES = [
        ('gemini', 'Gemini'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='provider_credentials')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('organization', 'provider')

    def __str__(self):
        return f"{self.get_provider_display()} credentials for {self.organization.name}"


class Occurrence(models.Model):
    """Represents an active incident, pentest, or CTF."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='occurrences')
    label = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=100, default='security')
    workflow = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.label} ({self.organization.name})"

class Evidence(models.Model):
    """Represents parsed data from attachments or chat, linked to an occurrence."""
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE, related_name='evidence')
    content = models.TextField()
    source_type = models.CharField(max_length=50)
    object_reference = models.CharField(max_length=1024)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Evidence for {self.occurrence.label} from {self.source_type}"

class Conversation(models.Model):
    """Represents a thread of execution, typically tied to a platform channel."""
    occurrence = models.ForeignKey(Occurrence, on_delete=models.SET_NULL, related_name='conversations', null=True, blank=True)
    platform_channel_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Conversation in channel {self.platform_channel_id}"

class Message(models.Model):
    """Represents a single turn in a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.role} message in {self.conversation.platform_channel_id}"

class BotIntegration(models.Model):
    """Stores credentials for third-party bot integrations."""
    PLATFORM_CHOICES = [
        ('discord', 'Discord'),
        ('slack', 'Slack'),
        ('mattermost', 'Mattermost'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='bot_integrations')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    bot_token = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('organization', 'platform')

    def __str__(self):
        return f"{self.get_platform_display()} integration for {self.organization.name}"

# --- Django Signals for Orchestration ---

@receiver(post_save, sender=BotIntegration)
def handle_bot_integration_save(sender, instance, created, **kwargs):
    """
    Fires when a BotIntegration is created or updated.
    """
    if instance.is_active:
        # If the bot is active, tell the fleet manager to start it.
        # This handles both new bots and bots being re-activated.
        publish_bot_command(
            action="start",
            bot_token=instance.bot_token,
            organization_id=instance.organization.id
        )
    else:
        # If the bot is marked as inactive, tell the fleet manager to stop it.
        publish_bot_command(
            action="stop",
            bot_token=instance.bot_token,
            organization_id=instance.organization.id
        )

@receiver(post_delete, sender=BotIntegration)
def handle_bot_integration_delete(sender, instance, **kwargs):
    """
    Fires when a BotIntegration is deleted.
    """
    # Tell the fleet manager to stop the bot.
    publish_bot_command(
        action="stop",
        bot_token=instance.bot_token,
        organization_id=instance.organization.id
    )

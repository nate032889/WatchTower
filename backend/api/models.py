from django.db import models
from django.utils import timezone

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
    key = models.CharField(max_length=255, unique=True) # In a real app, this would be hashed
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Key for {self.organization.name}"

class Occurrence(models.Model):
    """Represents an active incident, pentest, or CTF."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='occurrences')
    label = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=100, default='security')
    workflow = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='active') # e.g., active, closed
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.label} ({self.organization.name})"

class Evidence(models.Model):
    """Represents parsed data from attachments or chat, linked to an occurrence."""
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE, related_name='evidence')
    content = models.TextField()
    source_type = models.CharField(max_length=50) # e.g., pcap, text, binary
    object_reference = models.CharField(max_length=1024) # e.g., the Minio key
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
    role = models.CharField(max_length=20) # user, model, or system
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
    bot_token = models.CharField(max_length=255) # In a real app, use an encrypted field
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('organization', 'platform')

    def __str__(self):
        return f"{self.get_platform_display()} integration for {self.organization.name}"

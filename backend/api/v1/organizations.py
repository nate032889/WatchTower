from rest_framework import viewsets
from api.models import Organization
from api.serializers.organizations import OrganizationSerializer

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Organizations to be viewed or created.
    """
    queryset = Organization.objects.all().order_by('name')
    serializer_class = OrganizationSerializer

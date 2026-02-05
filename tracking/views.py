from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import TrackingCode
from .serializers import TrackingCodeSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def tracking_code_list(request):
    """Return active tracking codes for frontend injection. No auth required."""
    qs = TrackingCode.objects.filter(is_active=True).order_by('id')
    serializer = TrackingCodeSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

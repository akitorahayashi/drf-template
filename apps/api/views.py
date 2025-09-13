from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response


@require_GET
def health_check(request):  # noqa: ARG001
    """Simple health check endpoint."""
    return JsonResponse({"status": "ok"})


@api_view(["GET"])
def api_root(request):  # noqa: ARG001
    """Root API endpoint."""
    return Response({"message": "Welcome to drf-template API"})

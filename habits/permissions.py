from django.db.models import Model
from django.http import HttpRequest
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView


class IsHabitOwner(BasePermission):
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request: HttpRequest, view: APIView, obj: Model) -> bool:
        return bool(request.user.is_authenticated and obj.user == request.user)

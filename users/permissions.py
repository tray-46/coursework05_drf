from django.db.models import Model
from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView


class IsAccountOwner(BasePermission):

    def has_object_permission(self, request: HttpRequest, view: APIView, obj: Model) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user

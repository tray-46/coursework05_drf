from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.permissions import IsHabitOwner
from habits.serializers import HabitSerializer, PublicHabitSerializer


# Create your views here.
class HabitCreateAPIView(CreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitListAPIView(ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsHabitOwner]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Habit.objects.filter(user=self.request.user).order_by("id")
        return Habit.objects.none()


class PublicHabitListAPIView(ListAPIView):
    serializer_class = PublicHabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Habit.objects.filter(is_public=True).order_by("id")
        return Habit.objects.none()


class HabitRetrieveAPIView(RetrieveAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsHabitOwner]


class HabitUpdateAPIView(UpdateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsHabitOwner]

@extend_schema(
    description="Delete the specifies habit.",
    request=None,
    responses={
        204: OpenApiResponse(description="Habit successfully deleted."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Habit matches the given query."),
    },
)
class HabitDestroyAPIView(DestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsHabitOwner]

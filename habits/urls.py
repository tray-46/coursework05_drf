from django.urls import path

from habits import views
from habits.apps import HabitsConfig

app_name = HabitsConfig.name

urlpatterns = [
    path("habits/create/", views.HabitCreateAPIView.as_view(), name="habit-create"),
    path("habits/", views.HabitListAPIView.as_view(), name="habit-list"),
    path("habits/public/", views.PublicHabitListAPIView.as_view(), name="public-habit-list"),
    path("habits/<int:pk>/", views.HabitRetrieveAPIView.as_view(), name="habit-retrieve"),
    path("habits/<int:pk>/update/", views.HabitUpdateAPIView.as_view(), name="habit-update"),
    path("habits/<int:pk>/delete/", views.HabitDestroyAPIView.as_view(), name="habit-destroy"),
]

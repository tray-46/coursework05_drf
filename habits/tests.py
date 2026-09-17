from datetime import timedelta
from typing import Any
from unittest import TestCase
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from config.settings import TIME_ZONE
from habits.models import Action, Habit, Location, Reward
from users.models import User


# Create your tests here.
class HabitTest(APITestCase):

    def setUp(self) -> None:
        self.maxDiff = None

        dt_now = timezone.now()
        self.user1 = User.objects.create(username="user1", email="user1@habits.com", password="user1")
        self.user2 = User.objects.create(username="user2", email="user2@habits.com", password="user2")

        self.action_shower = Action.objects.create(name="Душ")
        self.action_running = Action.objects.create(name="Пробежка")
        self.action_cleaning = Action.objects.create(name="Уборка")

        self.location_home = Location.objects.create(name="Дом")
        self.location_stadium = Location.objects.create(name="Стадион")

        self.reward = Reward.objects.create(name="Сон")

        self.pleasant_habit_shower = Habit.objects.create(
            user=self.user1,
            action=self.action_shower,
            location=self.location_home,
            duration=120,
            execution_time=dt_now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=1),
            period=1,
            related_habit=None,
            reward=None,
            is_pleasant=True,
            is_public=False,
            is_disabled=False,
        )
        self.habit_running = Habit.objects.create(
            user=self.user1,
            action=self.action_running,
            location=self.location_stadium,
            duration=120,
            execution_time=dt_now.replace(hour=6, minute=30, second=0, microsecond=0) + timedelta(days=1),
            period=1,
            related_habit=self.pleasant_habit_shower,
            reward=None,
            is_pleasant=False,
            is_public=True,
            is_disabled=False,
        )
        self.habit_cleaning = Habit.objects.create(
            user=self.user1,
            action=self.action_cleaning,
            location=self.location_home,
            duration=60,
            execution_time=dt_now.replace(hour=20, minute=0, second=0, microsecond=0) + timedelta(days=1),
            period=1,
            related_habit=None,
            reward=self.reward,
            is_pleasant=False,
            is_public=True,
            is_disabled=False,
        )

    def test_create_habit(self) -> None:
        """
        Ensure we can create a new habit
        """
        dt_now = timezone.now()
        url = reverse("habits:habit-create")

        data = {
            "action": 1,
            "location": 2,
            "duration": 60,
            "execution_time": dt_now.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1),
            "period": 1,
            "related_habit": None,
            "reward": self.reward.pk,
            "is_pleasant": False,
            "is_public": True,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 4)

    def test_list_habits(self) -> None:
        url = reverse("habits:habit-list")
        result = {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.pleasant_habit_shower.pk,
                    "user": {
                        "id": self.pleasant_habit_shower.user.pk,
                        "username": self.pleasant_habit_shower.user.username,
                        "email": self.pleasant_habit_shower.user.email,
                    },
                    "action": {
                        "name": self.pleasant_habit_shower.action.name,
                    },
                    "location": {
                        "name": self.pleasant_habit_shower.location.name,
                    },
                    "duration": self.pleasant_habit_shower.duration,
                    "execution_time": self.pleasant_habit_shower.execution_time.astimezone(
                        ZoneInfo(TIME_ZONE)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "period": self.pleasant_habit_shower.period,
                    "related_habit": None,
                    "reward": None,
                    "is_pleasant": self.pleasant_habit_shower.is_pleasant,
                    "is_public": self.pleasant_habit_shower.is_public,
                    "is_disabled": self.pleasant_habit_shower.is_disabled,
                },
                {
                    "id": self.habit_running.pk,
                    "user": {
                        "id": self.habit_running.user.pk,
                        "username": self.habit_running.user.username,
                        "email": self.habit_running.user.email,
                    },
                    "action": {
                        "name": self.habit_running.action.name,
                    },
                    "location": {
                        "name": self.habit_running.location.name,
                    },
                    "duration": self.habit_running.duration,
                    "execution_time": self.habit_running.execution_time.astimezone(ZoneInfo(TIME_ZONE)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "period": self.habit_running.period,
                    "related_habit": {
                        "id": self.pleasant_habit_shower.pk,
                        "user": {
                            "id": self.pleasant_habit_shower.user.pk,
                            "username": self.pleasant_habit_shower.user.username,
                            "email": self.pleasant_habit_shower.user.email,
                        },
                        "action": {
                            "name": self.pleasant_habit_shower.action.name,
                        },
                        "location": {
                            "name": self.pleasant_habit_shower.location.name,
                        },
                        "duration": self.pleasant_habit_shower.duration,
                        "execution_time": self.pleasant_habit_shower.execution_time.astimezone(
                            ZoneInfo(TIME_ZONE)
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "period": self.pleasant_habit_shower.period,
                        "related_habit": None,
                        "reward": None,
                        "is_pleasant": self.pleasant_habit_shower.is_pleasant,
                        "is_public": self.pleasant_habit_shower.is_public,
                        "is_disabled": self.pleasant_habit_shower.is_disabled,
                    },
                    "reward": None,
                    "is_pleasant": self.habit_running.is_pleasant,
                    "is_public": self.habit_running.is_public,
                    "is_disabled": self.habit_running.is_disabled,
                },
                {
                    "id": self.habit_cleaning.pk,
                    "user": {
                        "id": self.habit_cleaning.user.pk,
                        "username": self.habit_cleaning.user.username,
                        "email": self.habit_cleaning.user.email,
                    },
                    "action": {
                        "name": self.habit_cleaning.action.name,
                    },
                    "location": {
                        "name": self.habit_cleaning.location.name,
                    },
                    "duration": self.habit_cleaning.duration,
                    "execution_time": self.habit_cleaning.execution_time.astimezone(ZoneInfo(TIME_ZONE)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "period": self.habit_cleaning.period,
                    "related_habit": None,
                    "reward": {
                        "name": self.habit_cleaning.reward.name if self.habit_cleaning.reward else None,
                    },
                    "is_pleasant": self.habit_cleaning.is_pleasant,
                    "is_public": self.habit_cleaning.is_public,
                    "is_disabled": self.habit_cleaning.is_disabled,
                },
            ],
        }
        empty_result: dict[str, Any] = {"count": 0, "next": None, "previous": None, "results": []}

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, empty_result)

    def test_retrieve_habit(self) -> None:
        url = reverse("habits:habit-retrieve", args=[self.pleasant_habit_shower.pk])
        result = {
            "id": self.pleasant_habit_shower.pk,
            "user": {
                "id": self.pleasant_habit_shower.user.pk,
                "username": self.pleasant_habit_shower.user.username,
                "email": self.pleasant_habit_shower.user.email,
            },
            "action": {
                "name": self.pleasant_habit_shower.action.name,
            },
            "location": {
                "name": self.pleasant_habit_shower.location.name,
            },
            "duration": self.pleasant_habit_shower.duration,
            "execution_time": self.pleasant_habit_shower.execution_time.astimezone(ZoneInfo(TIME_ZONE)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "period": self.pleasant_habit_shower.period,
            "related_habit": None,
            "reward": None,
            "is_pleasant": self.pleasant_habit_shower.is_pleasant,
            "is_public": self.pleasant_habit_shower.is_public,
            "is_disabled": self.pleasant_habit_shower.is_disabled,
        }

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_habit(self) -> None:
        url = reverse("habits:habit-update", args=[self.pleasant_habit_shower.pk])

        data = {
            "duration": 60,
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("duration"), data.get("duration"))

        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_habit(self) -> None:
        url = reverse("habits:habit-destroy", args=[self.habit_cleaning.pk])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 2)


class ModelsTest(TestCase):

    def setUp(self) -> None:
        dt_now = timezone.now()
        self.execution_time = dt_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.user = User(username="user1", email="user1@habits.com", password="user1")
        self.action = Action(name="test_action")
        self.location = Location(name="test_location")
        self.reward = Reward(name="test_reward")
        self.habit = Habit(
            user=self.user,
            action=self.action,
            location=self.location,
            duration=1,
            execution_time=self.execution_time,
            period=1,
            is_pleasant=True,
        )

    def test_action_str(self) -> None:
        self.assertEqual(str(self.action), "test_action")

    def test_location_str(self) -> None:
        self.assertEqual(str(self.location), "test_location")

    def test_reward_str(self) -> None:
        self.assertEqual(str(self.reward), "test_reward")

    def test_habit_str(self) -> None:
        self.assertEqual(
            str(self.habit),
            f"{self.action.name} {self.execution_time.astimezone().strftime('%H:%M')} {self.location.name}",
        )

    def test_invalid_execution_time(self) -> None:
        self.habit.execution_time -= timedelta(days=1)

        with self.assertRaises(ValidationError):
            self.habit.full_clean()

    def test_invalid_related_habit(self) -> None:
        related_habit = Habit(
            user=self.user,
            action=self.action,
            location=self.location,
            duration=1,
            execution_time=self.execution_time,
            period=1,
            is_pleasant=False,
        )
        self.habit.related_habit = related_habit

        with self.assertRaises(ValidationError):
            self.habit.full_clean()

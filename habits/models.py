from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from users.models import User


# Create your models here.
class Action(models.Model):
    """
    Represent an action.
    """

    name = models.CharField(max_length=250, unique=True, verbose_name="Действие")

    class Meta:
        verbose_name = "Действие"
        verbose_name_plural = "Действия"

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    """
    Represent a location.
    """

    name = models.CharField(max_length=250, unique=True, verbose_name="Место")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self) -> str:
        return self.name


class Reward(models.Model):
    """
    Represent a reward.
    """

    name = models.CharField(max_length=250, unique=True, verbose_name="Вознаграждение")

    class Meta:
        verbose_name = "Награда"
        verbose_name_plural = "Награды"

    def __str__(self) -> str:
        return self.name


class Habit(models.Model):
    """
    Represent a habit.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits", verbose_name="Пользователь")
    action = models.ForeignKey(Action, on_delete=models.RESTRICT, related_name="habits", verbose_name="Действие")
    location = models.ForeignKey(Location, on_delete=models.RESTRICT, related_name="habits", verbose_name="Место")
    duration = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)], verbose_name="Время на выполнение (в секундах)"
    )
    execution_time = models.DateTimeField(default=timezone.now, verbose_name="Следующее выполнение")
    period = models.SmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(7)], verbose_name="Периодичность"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"is_pleasant": True},
        error_messages={"invalid": "Selected habit is invalid. Please select pleasant habit."},
        verbose_name="Связаная привычка",
    )
    reward = models.ForeignKey(
        Reward, on_delete=models.RESTRICT, null=True, blank=True, related_name="habits", verbose_name="Вознаграждение"
    )
    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")
    is_public = models.BooleanField(default=False, verbose_name="Признак публичной привычки")
    is_disabled = models.BooleanField(default=False, verbose_name="Отключена")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(is_pleasant=True, related_habit__isnull=True, reward__isnull=True)
                    | models.Q(is_pleasant=False, related_habit__isnull=False, reward__isnull=True)
                    | models.Q(is_pleasant=False, related_habit__isnull=True, reward__isnull=False)
                ),
                name="pleasant_habit_or_related_habit_or_reward",
                violation_error_message="Pleasant habit can't have either relate_habit or reward. "
                "Useful habit can have either related habit or reward",
            ),
            models.CheckConstraint(
                condition=models.Q(duration__gte=1) & models.Q(duration__lte=120),
                name="duration_range_1_to_120",
                violation_error_message="Duration cand be more than 120 seconds.",
            ),
            models.CheckConstraint(
                condition=models.Q(period__gte=1) & models.Q(period__lte=7),
                name="period_range_1_to_7",
                violation_error_message="Habit should be performed at least once a week.",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.action.name} {self.execution_time.astimezone().strftime('%H:%M')} {self.location.name}"

    def clean(self) -> None:
        super().clean()

        if self.execution_time and self.execution_time < timezone.now():
            raise ValidationError({"execution_time": "The date cannot be in the past."})

        if self.related_habit:
            if not self.related_habit.is_pleasant:
                raise ValidationError({"related_habit": "related_habit can be only pleasant habit"})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

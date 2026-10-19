# import os
# import django
#
# # Replace 'your_project_name' with the folder name containing your settings.py
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# django.setup()
import os

import requests
from datetime import timedelta

from django.db.models import QuerySet
from django.utils import timezone

from config.settings import DEBUG
from habits.models import Habit

TG_BOT_API_KEY = os.environ.get("TG_BOT_API_KEY")


def send_telegram_message(chat_id: str, message: str) -> None:
    if DEBUG:
        print(f"telegram message to {chat_id}: {message}")
    else:
        if not TG_BOT_API_KEY:
            raise RuntimeError("TG_BOT_API_KEY not set")

        params = {"chat_id": chat_id, "text": message}

        response = requests.post(
            f"https://api.telegram.org/bot{TG_BOT_API_KEY}/sendMessage",
            params=params,
            timeout=10
        )

        response.raise_for_status()


def get_habits_to_notify() -> QuerySet[Habit]:
    dt_now = timezone.now()
    one_hour_from_now = dt_now + timedelta(hours=1)
    habits_to_notify = Habit.objects.filter(
        is_disabled=False, execution_time__range=(dt_now, one_hour_from_now)
    ).order_by("execution_time")
    return habits_to_notify


if __name__ == "__main__":
    # habits = get_habits_to_notify()
    # print(habits)
    pass

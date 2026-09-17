# import os
# import django
#
# # Replace 'your_project_name' with the folder name containing your settings.py
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# django.setup()
import os

import requests
from datetime import timedelta

from django.utils import timezone

from habits.models import Habit


TG_BOT_API_KEY = os.environ.get("TG_BOT_API_KEY")


def send_telegram_message(chat_id, message):
    # params = {"chat_id": chat_id, "text": message}
    # requests.get(f"https://api.telegram.org/bot{TG_BOT_API_KEY}/sendMessage", params=params)
    print(f"telegram message to {chat_id}: {message}")


def get_habits_to_notify():
    dt_now = timezone.now()
    one_hour_from_now = dt_now + timedelta(hours=1)
    habits_to_notify = Habit.objects.filter(is_disabled=False, execution_time__range=(dt_now, one_hour_from_now)).order_by('execution_time')
    return habits_to_notify


if __name__ == "__main__":
    # habits = get_habits_to_notify()
    # print(habits)
    pass
# import os
# import django
#
# # Replace 'your_project_name' with the folder name containing your settings.py
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# django.setup()

from datetime import timedelta

from celery import shared_task

from habits.models import Habit
from habits.services import get_habits_to_notify, send_telegram_message


@shared_task
def send_habit_notification_task() -> None:
    habits_to_notify = get_habits_to_notify()
    for habit in habits_to_notify:
        execution_time = habit.execution_time.astimezone().time().strftime("%H:%M")
        reward = "" if habit.is_pleasant else f" reward: {habit.reward if habit.reward else habit.related_habit}"
        message = f"{execution_time} {habit.location} {habit.action}{reward}"
        if habit.user.telegram_chat_id:
            send_telegram_message(habit.user.telegram_chat_id, message)
        habit.execution_time = habit.execution_time + timedelta(days=habit.period)
    Habit.objects.bulk_update(habits_to_notify, ["execution_time"])


if __name__ == "__main__":
    # send_habit_notification_task()
    pass

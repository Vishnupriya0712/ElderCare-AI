
from datetime import datetime


def get_due_medicine_reminders(reminders):

    current_time = datetime.now()

    due_reminders = []

    for reminder in reminders:

        try:
            reminder_time = datetime.strptime(
                reminder["time"], "%H:%M"
            ).time()

            if (
                reminder_time.hour == current_time.hour
                and reminder_time.minute == current_time.minute
            ):
                due_reminders.append(reminder)

        except (KeyError, ValueError):
            continue

    return due_reminders


def get_due_activities(schedule):

    current_time = datetime.now()

    due_activities = []

    for activity in schedule:

        try:
            activity_datetime = datetime.strptime(
                activity["date"] + " " + activity["time"],
                "%Y-%m-%d %H:%M"
            )

            if (
                activity_datetime.date() == current_time.date()
                and activity_datetime.hour == current_time.hour
                and activity_datetime.minute == current_time.minute
            ):
                due_activities.append(activity)

        except (KeyError, ValueError):
            continue

    return due_activities

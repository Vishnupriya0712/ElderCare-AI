
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "reminders.json")


def load_reminders():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                reminders = json.load(file)

            if not isinstance(reminders, list):
                return []

            # Support older reminders without a taken status
            for reminder in reminders:
                reminder.setdefault("taken", False)

            return reminders

        except (json.JSONDecodeError, OSError):
            return []

    return []


def save_reminders(reminders):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(reminders, file, indent=4)


def add_reminder(medicine, dosage, reminder_time):
    reminders = load_reminders()

    new_reminder = {
        "medicine": medicine,
        "dosage": dosage,
        "time": reminder_time,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "taken": False
    }

    reminders.append(new_reminder)
    save_reminders(reminders)

    return new_reminder


def mark_as_taken(index, taken=True):
    reminders = load_reminders()

    if 0 <= index < len(reminders):
        reminders[index]["taken"] = taken
        save_reminders(reminders)
        return True

    return False


def delete_reminder(index):
    reminders = load_reminders()

    if 0 <= index < len(reminders):
        reminders.pop(index)
        save_reminders(reminders)
        return True

    return False

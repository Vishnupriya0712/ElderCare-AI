
import json
import os
from datetime import datetime

SCHEDULE_FILE = "daily_schedule.json"


# Load saved activities
def load_schedule():

    if os.path.exists(SCHEDULE_FILE):

        try:
            with open(SCHEDULE_FILE, "r") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return []

    return []


# Save activities
def save_schedule(schedule):

    with open(SCHEDULE_FILE, "w") as file:
        json.dump(schedule, file, indent=4)


# Add a new activity
def add_activity(activity, activity_date, activity_time, description):

    schedule = load_schedule()

    new_activity = {
        "activity": activity,
        "date": activity_date,
        "time": activity_time,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    schedule.append(new_activity)

    save_schedule(schedule)

    return new_activity


# Delete an activity
def delete_activity(index):

    schedule = load_schedule()

    if 0 <= index < len(schedule):

        schedule.pop(index)

        save_schedule(schedule)

        return True

    return False

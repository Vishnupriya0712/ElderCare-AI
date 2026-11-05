
import json
import os
from datetime import datetime

CHAT_FILE = "chat_history.json"


def load_chat_history():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    return []


def save_chat(messages, session_id):
    history = load_chat_history()

    existing_chat = next(
        (chat for chat in history if chat["session_id"] == session_id),
        None
    )

    if existing_chat:
        existing_chat["messages"] = messages
        existing_chat["updated_at"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else:
        history.append({
            "session_id": session_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": messages
        })

    with open(CHAT_FILE, "w") as file:
        json.dump(history, file, indent=4)


def clear_chat_history():
    with open(CHAT_FILE, "w") as file:
        json.dump([], file, indent=4)

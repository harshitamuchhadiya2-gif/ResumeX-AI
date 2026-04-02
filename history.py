import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}

    with open(HISTORY_FILE, "r") as file:
        try:
            data = json.load(file)
            if isinstance(data, dict):
                return data
            return {}
        except:
            return {}


def save_all_history(data):
    with open(HISTORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def save_history(username, record):
    history = load_history()

    if username not in history:
        history[username] = []

    record["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history[username].append(record)

    save_all_history(history)


def get_user_history(username):
    history = load_history()
    return history.get(username, [])


def clear_user_history(username):
    history = load_history()
    history[username] = []
    save_all_history(history)

import os
from datetime import datetime

LOG_FILE = "logs.txt"


def log_action(user_id: str, action: str, details: str = ""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{timestamp}, {user_id or 'anonymous'}, {action.strip()}"
    if details:
        linea += f", {details.strip()}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
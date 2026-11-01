"""
Random publishing schedule for the LP Tuning auto blog.

The GitHub Action runs this several times a day. It only lets a post through
when the saved "next_publish_at" time has passed. After a post goes out, the
next one is set a random 3 to 6 days later at a random hour, so posts never
land on a fixed weekday or time.

Usage:
  python scripts/blog_schedule.py check    -> prints publish=true/false to $GITHUB_OUTPUT
  python scripts/blog_schedule.py advance  -> sets the next random publish time
"""
import datetime
import json
import os
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(BASE_DIR, "scripts", "blog_schedule.json")
MIN_DAYS, MAX_DAYS = 3, 6


def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def load() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def random_next(start: datetime.datetime) -> datetime.datetime:
    days = random.randint(MIN_DAYS, MAX_DAYS)
    target = (start + datetime.timedelta(days=days)).replace(
        hour=random.randint(0, 23), minute=random.randint(0, 59), second=0, microsecond=0
    )
    return target


def set_output(key: str, value: str):
    out = os.environ.get("GITHUB_OUTPUT")
    line = f"{key}={value}"
    if out:
        with open(out, "a") as f:
            f.write(line + "\n")
    print(line)


def check():
    state = load()
    due_str = state.get("next_publish_at")
    if not due_str:
        set_output("publish", "true")
        return
    due = datetime.datetime.fromisoformat(due_str)
    set_output("publish", "true" if now_utc() >= due else "false")
    print(f"Next post due: {due_str}")


def advance():
    state = load()
    state["last_published_at"] = now_utc().isoformat(timespec="minutes")
    state["next_publish_at"] = random_next(now_utc()).isoformat(timespec="minutes")
    save(state)
    print(f"Next post scheduled for {state['next_publish_at']}")


if __name__ == "__main__":
    {"check": check, "advance": advance}[sys.argv[1] if len(sys.argv) > 1 else "check"]()

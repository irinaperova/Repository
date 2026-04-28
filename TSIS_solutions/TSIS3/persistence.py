import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
SETTINGS_FILE = BASE / "settings.json"
LEADERBOARD_FILE = BASE / "leaderboard.json"
DEFAULT_SETTINGS = {"sound": True, "car_color": "blue", "difficulty": "normal"}


def load_json(path, default):
    if not path.exists():
        path.write_text(json.dumps(default, indent=2))
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return default.copy() if isinstance(default, dict) else list(default)


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))


def load_settings():
    data = load_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())
    for k, v in DEFAULT_SETTINGS.items():
        data.setdefault(k, v)
    return data


def save_settings(data):
    save_json(SETTINGS_FILE, data)


def load_scores():
    return load_json(LEADERBOARD_FILE, [])


def save_score(name, score, distance, coins):
    scores = load_scores()
    scores.append({"name": name or "Player", "score": int(score), "distance": int(distance), "coins": int(coins)})
    scores.sort(key=lambda x: x["score"], reverse=True)
    save_json(LEADERBOARD_FILE, scores[:10])

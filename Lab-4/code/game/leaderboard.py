import json
import os

MAX_ENTRIES = 5
DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leaderboard.json"
)


def load(path=DEFAULT_PATH):
    """Return {difficulty: [best times ascending]}. A missing or damaged file
    simply gives an empty leaderboard."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    clean = {}
    for name, times in data.items():
        if isinstance(times, list):
            good = [float(t) for t in times
                    if isinstance(t, (int, float)) and not isinstance(t, bool)]
            clean[str(name)] = sorted(good)[:MAX_ENTRIES]
    return clean


def save(data, path=DEFAULT_PATH):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def add_time(difficulty, seconds, path=DEFAULT_PATH):
    """Record a finishing time for a difficulty tier.
    Returns (top_times, rank) where rank is the 0-based position of the new
    time in the top list, or None if it did not make the top 5."""
    seconds = round(float(seconds), 2)
    data = load(path)
    times = data.get(difficulty, [])
    times.append(seconds)
    times.sort()
    times = times[:MAX_ENTRIES]
    data[difficulty] = times
    try:
        save(data, path)
    except OSError:
        pass  # keep playing even if the file can't be written
    rank = times.index(seconds) if seconds in times else None
    return times, rank

import json
from datetime import date
from pathlib import Path


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def seconds_to_hours(seconds: int) -> float:
    return (seconds or 0) / 3600.0


def summarize_by_sport(activities: list[dict]) -> list[str]:
    by_type: dict[str, dict[str, int]] = {}

    for a in activities:
        sport = a.get("type") or a.get("sport") or "Unknown"
        moving_time = int(a.get("moving_time") or a.get("movingTime") or 0)

        if sport not in by_type:
            by_type[sport] = {"count": 0, "seconds": 0}

        by_type[sport]["count"] += 1
        by_type[sport]["seconds"] += moving_time

    lines = []
    for sport in sorted(by_type.keys()):
        c = by_type[sport]["count"]
        h = seconds_to_hours(by_type[sport]["seconds"])
        lines.append(f"- {sport}: {c} sessions, {h:.1f} h")

    return lines


def main():
    activities = load_json("data/activities_14d.json")
    wellness = load_json("data/wellness_14d.json")

    out_dir = Path("output/weekly")
    out_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()

    md = []
    md.append(f"# Weekly Summary ({today})")
    md.append("")
    md.append("## Last 14 days (by sport)")
    md.extend(summarize_by_sport(activities))
    md.append("")
    md.append("## Wellness records (last 14 days)")
    md.append(f"- Records: {len(wellness)}")
    md.append("")

    out_file = out_dir / f"weekly_{today}.md"
    out_file.write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
import os
import json
from datetime import date
from pathlib import Path
import anthropic


MODEL = "claude-sonnet-4-6"

RACE_DATE = "2026-08-30"
RACE_NAME = "TCS Sydney Marathon"


def load_json(path: str) -> str:
    """Load JSON and return compact string (saves tokens vs pretty-print)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, separators=(",", ":"))


def weeks_to_race(today: date) -> int:
    race = date.fromisoformat(RACE_DATE)
    return max(0, (race - today).days // 7)


def main():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = date.today()
    today_str = today.isoformat()
    weekly_path = Path(f"output/weekly/weekly_{today_str}.md")
    activities_path = Path("data/activities_28d.json")
    wellness_path = Path("data/wellness_28d.json")
    planned_week_path = Path("data/planned_week.md")

    if not weekly_path.exists():
        raise FileNotFoundError(f"{weekly_path} not found — run weekly_report.py first")

    weekly_md = weekly_path.read_text(encoding="utf-8")

    # Raw data blocks
    activities_block = ""
    if activities_path.exists():
        activities_block = f"\n\n### Raw activity data (28 days)\n```json\n{load_json(activities_path)}\n```"

    wellness_block = ""
    if wellness_path.exists():
        wellness_block = f"\n\n### Raw wellness data (28 days)\n```json\n{load_json(wellness_path)}\n```"

    # Planned week from Runna
    planned_block = ""
    if planned_week_path.exists():
        planned = planned_week_path.read_text(encoding="utf-8").strip()
        planned_block = f"\n\n### Planned week (from Runna)\n{planned}"
    else:
        planned_block = "\n\n### Planned week\n_No planned_week.md found — compliance analysis skipped._"

    weeks_out = weeks_to_race(today)

    prompt = f"""You are a data-driven marathon coach reviewing an athlete's training data.

## Athlete profile
- Goal race: {RACE_NAME} on {RACE_DATE} ({weeks_out} weeks away)
- Goal: Sub 3:30 (target pace ~4:58/km)
- Currently: Start of marathon training block
- Location: Canberra, Australia
- Weight: 102 kg
- Max HR: 198 bpm, LTHR: 180 bpm, Resting HR: ~47 bpm
- Strength training: ongoing, athlete manages this independently — do not prescribe strength sessions
- Training load metrics: ATL (acute/7-day fatigue), CTL (chronic/42-day fitness), Form = CTL minus ATL

## Data provided
### High-level summary
{weekly_md}
{activities_block}
{wellness_block}
{planned_block}

## Your task
Produce a coaching report with these four sections:

### 1. Key takeaways
Summarise training load trend (ATL vs CTL / form), run volume, and standout sessions. 
Reference actual HR zones, pacing, cadence, HRV, and sleep where the data supports it.
Flag how this week fits into the broader 14-week marathon build toward {RACE_DATE}.

### 2. Planned vs actual compliance
Compare what was planned (Runna) against what was actually completed.
For each planned session: was it done, modified, or missed? What was the impact on load?
If no plan is provided, skip this section.

### 3. Coaching notes for next week
Do NOT prescribe specific sessions — the athlete follows Runna for that.
Instead provide 3–5 specific, actionable notes to guide execution of next week's Runna sessions. 
Examples: pacing targets, HR caps, cadence cues, recovery focus, heat management, sleep priority.
Frame these around what the data is telling you and the sub-3:30 goal.

### 4. One metric to monitor
The single most important metric to watch this coming week and why.

Keep language direct and coach-like. Use markdown. Be specific — reference actual numbers from the data.
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    coaching_text = message.content[0].text

    out_path = Path(f"output/weekly/coaching_{today_str}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(coaching_text, encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"Tokens used — input: {message.usage.input_tokens}, output: {message.usage.output_tokens}")
    print(f"Weeks to {RACE_NAME}: {weeks_out}")


if __name__ == "__main__":
    main()
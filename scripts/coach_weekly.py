import os
import json
from datetime import date
from pathlib import Path
import anthropic


MODEL = "claude-sonnet-4-6"


def load_json(path: str) -> str:
    """Load JSON and return compact string (saves tokens vs pretty-print)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, separators=(",", ":"))


def main():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = date.today().isoformat()
    weekly_path = Path(f"output/weekly/weekly_{today}.md")
    activities_path = Path("data/activities_28d.json")
    wellness_path = Path("data/wellness_28d.json")

    if not weekly_path.exists():
        raise FileNotFoundError(f"{weekly_path} not found — run weekly_report.py first")

    weekly_md = weekly_path.read_text(encoding="utf-8")

    # Include raw data if available — gives Claude real numbers to work with
    activities_block = ""
    if activities_path.exists():
        activities_block = f"\n\n### Raw activity data (28 days)\n```json\n{load_json(activities_path)}\n```"

    wellness_block = ""
    if wellness_path.exists():
        wellness_block = f"\n\n### Raw wellness data (28 days)\n```json\n{load_json(wellness_path)}\n```"

    prompt = f"""You are a data-driven endurance coach reviewing an athlete's last 28 days of training data.

## Athlete profile
- Sport: Triathlon (currently), transitioning to marathon block mid-year
- Location: Canberra, Australia
- Weight: 102 kg
- Max HR: 198 bpm, LTHR: 180 bpm, Resting HR: ~47 bpm
- Bike FTP: 210 W (where available)
- Training load metrics use ATL (acute, 7-day) and CTL (chronic, 42-day fitness)

## Data provided
### High-level summary
{weekly_md}
{activities_block}
{wellness_block}

## Your task
Analyse the data and produce a coaching report with these sections:

### 1. Key takeaways
Summarise training load trend (ATL vs CTL / form), volume by sport, and any standout sessions. Call out HR zones, pacing, cadence, or HRV patterns where the data supports it.

### 2. Risk assessment
Identify any red flags: overreaching, HRV suppression, poor sleep, imbalanced sport mix, lack of easy days, HR drift, or injury risk. Be specific — reference actual values.

### 3. Next-week structure (Mon–Sun)
Propose a concrete 7-day plan. Include sport, rough duration, and the purpose of each session (e.g. aerobic base, threshold, recovery). Factor in current form and fatigue.

### 4. One metric to monitor
Name the single most important metric to watch this week and why, given the current training state.

Keep language direct and practical. Use markdown formatting.
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    coaching_text = message.content[0].text

    out_path = Path(f"output/weekly/coaching_{today}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(coaching_text, encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"Tokens used — input: {message.usage.input_tokens}, output: {message.usage.output_tokens}")


if __name__ == "__main__":
    main()
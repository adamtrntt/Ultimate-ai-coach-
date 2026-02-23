import os
from datetime import date
from pathlib import Path

from openai import OpenAI


MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def main():
    client = OpenAI()  # uses OPENAI_API_KEY from env :contentReference[oaicite:2]{index=2}

    today = date.today().isoformat()
    weekly_path = Path(f"output/weekly/weekly_{today}.md")
    if not weekly_path.exists():
        raise FileNotFoundError(f"Missing {weekly_path}. Did weekly_report.py run?")

    weekly = weekly_path.read_text(encoding="utf-8")

    prompt = f"""You are a data-driven endurance coach.

Athlete:
- Current: triathlon training
- Will switch to a marathon block mid-year
- Wants practical guidance for the next 7 days

Input summary:
{weekly}

Return markdown with:
1) Key takeaways (3-6 bullets)
2) Risk flags (overload/imbalance/recovery)
3) Next-week structure (Mon–Sun): swim/bike/run + intent (easy/quality/long)
4) One focus metric to watch next week
"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a conservative endurance coach. Do not prescribe unsafe training."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )  # chat.completions.create is the documented call :contentReference[oaicite:3]{index=3}

    out_text = resp.choices[0].message.content.strip()

    out_path = Path(f"output/weekly/coaching_{today}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
import os
from datetime import date
from pathlib import Path
import google.generativeai as genai

MODEL = "models/gemini-1.5-pro-latest"  

def main():
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(MODEL)

    today = date.today().isoformat()
    weekly_path = Path(f"output/weekly/weekly_{today}.md")

    if not weekly_path.exists():
        raise FileNotFoundError(f"{weekly_path} not found")

    weekly = weekly_path.read_text(encoding="utf-8")

    prompt = f"""
You are a data-driven endurance coach.

Athlete:
- Currently training for triathlon
- Will transition to marathon block mid-year
- Based in Canberra

Here is the last 28-day training summary:

{weekly}

Provide markdown output with:

1) Key takeaways
2) Risk assessment
3) Suggested next-week structure (Mon–Sun)
4) One metric to monitor
"""

    response = model.generate_content(prompt)
    coaching_text = response.text

    out_path = Path(f"output/weekly/coaching_{today}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(coaching_text)

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
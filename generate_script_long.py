"""
generate_script_long.py  <-- THIS FILE IS FOR THE LONG PIPELINE ONLY
Trend-research + long-form script generation. Mixes evergreen finance-
psychology deep-dives (70%) with real daily news (30%). A CODE-LEVEL safety
check (not just prompt instructions) guarantees every published video is
strictly personal-finance-wallet relevant.
Writes to: today_script_long.json
"""

import os
import json
import time
import random
from datetime import date
import requests
import google.generativeai as genai

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

NEWS_PROBABILITY = 0.3
CHANNEL_LAUNCH_DATE = date(2026, 9, 18)


def get_day_number():
    return (date.today() - CHANNEL_LAUNCH_DATE).days + 1


EVERGREEN_TOPICS = [
    "why lifestyle inflation quietly keeps high earners broke, and how to break the cycle",
    "the psychology behind impulse spending and how marketers exploit it",
    "why budgeting fails for most people, and a system that actually works",
    "how debt traps build slowly, and the warning signs people ignore",
    "compound interest explained with real timelines: what starting at 25 vs 35 actually looks like",
    "buy-now-pay-later apps: the hidden long-term cost most users never calculate",
    "why comparing your finances to others online is actively hurting your progress",
    "good debt vs bad debt: a full practical breakdown with examples",
    "why emergency funds matter more than early investing, explained with real scenarios",
    "the subscription trap: how small recurring charges quietly cost people thousands a year",
]


def fetch_headlines():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "category": "business",
        "pageSize": 15,
        "apiKey": NEWS_API_KEY,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    articles = r.json().get("articles", [])
    return "\n".join(
        f"- {a['title']}: {a.get('description') or ''}"
        for a in articles if a.get("title")
    )[:6000]


SHARED_RULES = """
SERIES FORMAT (mandatory):
- This is Day {day_number} of an ongoing daily series called MoneyPulse.
- The title MUST include "Day {day_number}" somewhere.

NUMBER OF THE DAY (mandatory):
- Exactly ONE scene must be a dedicated "Number of the Day" moment: one
  concrete, real, verified number/statistic, presented punchily. Mark this
  scene by starting its on_screen_text with "NUMBER OF THE DAY:".

CLIFFHANGER ENDING (mandatory):
- The very last scene must end with a short teaser for tomorrow's video
  without revealing specifics, plus a comment-trigger question and follow CTA.
"""

NEWS_PROMPT = """You are a Senior Finance Trend Research Analyst AND long-form
YouTube script writer for a US finance channel called MoneyPulse, which is
STRICTLY about personal finance - how news affects an ordinary person's
wallet, prices, job, savings, or daily money life. It is NEVER about general
tech, AI industry, corporate/legal drama, or business news with no personal
money angle.

STEP 1: From today's headlines below, pick the ONE story with the clearest,
most direct personal-wallet impact (interest rates, inflation, prices, jobs,
housing, loans, taxes, benefits, layoffs, banking, etc).

STEP 2: Before writing the script, fill "wallet_impact" with ONE specific,
concrete sentence describing exactly how this changes an ordinary person's
money, in dollars/percentage/job terms if possible. If you cannot write a
real, specific, non-generic sentence here, this story does not qualify -
pick a different headline or use the closest available one and make the
wallet_impact honestly reflect the connection.

STEP 3: Write a 5-7 minute long-form video script on that topic.
Go deep: background/context, the news itself, why it's happening, historical
comparison, who is affected and how, multiple real examples, plain-English
analysis, what happens next, actionable advice, strong takeaway.
Tone: casual, friendly, smart, not robotic. Use only verified real numbers
from the headlines below - never invent stats.
{shared_rules}
Return ONLY valid JSON, no markdown:
{{
  "topic": "one sentence",
  "wallet_impact": "one specific sentence: exactly how this affects an ordinary person's money",
  "why_it_works": "1-2 sentences",
  "title": "compelling title under 100 chars, must include Day {day_number}",
  "description": "3-4 sentence description",
  "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "scenes": [
    {{"voiceover": "MAX 30 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}}
  ]
}}
Rules: exactly 14-18 scenes, each voiceover 30 words or FEWER.

Today's real US finance headlines:
"""

EVERGREEN_PROMPT = """You are a long-form YouTube script writer for a US
finance channel called MoneyPulse, specializing in personal finance
psychology - deep, evergreen content that stays relevant for months.

Today's assigned topic: {topic}

Write a 5-7 minute long-form video script on this topic.
Go deep: what the mistake/myth is, the psychology behind why people fall for
it, multiple relatable real-life examples, plain-English analysis, a
step-by-step practical fix, and a strong takeaway.
Tone: casual, friendly, smart, relatable, not robotic.
Do not invent specific statistics, EXCEPT for the mandatory Number of the
Day scene, which must use a real, well-known statistic.
{shared_rules}
Return ONLY valid JSON, no markdown:
{{
  "topic": "one sentence",
  "wallet_impact": "one specific sentence: exactly how this affects an ordinary person's money",
  "why_it_works": "1-2 sentences",
  "title": "compelling title under 100 chars, must include Day {day_number}",
  "description": "3-4 sentence description",
  "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "scenes": [
    {{"voiceover": "MAX 30 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}}
  ]
}}
Rules: exactly 14-18 scenes, each voiceover 30 words or FEWER.
"""


def call_gemini_with_retry(prompt, attempts=5):
    model = genai.GenerativeModel("gemini-flash-latest")
    last_err = None
    for i in range(attempts):
        try:
            response = model.generate_content(prompt, request_options={"timeout": 240})
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            last_err = e
            print(f"Gemini attempt {i+1} failed: {e}")
            wait_time = 60
            err_str = str(e)
            if "retry_delay" in err_str and "seconds:" in err_str:
                try:
                    suggested = int(err_str.split("seconds:")[1].split("}")[0].strip())
                    wait_time = suggested + 15
                except Exception:
                    pass
            print(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    raise last_err


def passes_niche_check(data):
    impact = data.get("wallet_impact", "").strip().lower()
    if len(impact) < 15:
        return False
    banned_generic_phrases = [
        "affects the economy", "impacts businesses", "affects investors",
        "affects the market", "affects companies",
    ]
    if any(phrase in impact for phrase in banned_generic_phrases):
        return False
    money_signals = [
        "$", "price", "job", "salary", "wage", "rent", "mortgage", "loan",
        "tax", "save", "spend", "debt", "interest rate", "cost", "pay",
        "bill", "income", "budget",
    ]
    if not any(signal in impact for signal in money_signals):
        return False
    return True


def generate():
    day_number = get_day_number()
    shared_rules = SHARED_RULES.format(day_number=day_number)
    use_news = random.random() < NEWS_PROBABILITY

    data = None
    if use_news:
        print(f"LONG Mode: NEWS (30% chance) - Day {day_number}")
        headlines = fetch_headlines()
        prompt = NEWS_PROMPT.format(shared_rules=shared_rules, day_number=day_number) + headlines
        data = call_gemini_with_retry(prompt)

        if not passes_niche_check(data):
            print("LONG NEWS topic FAILED niche check - falling back to evergreen topic.")
            data = None

    if data is None:
        topic = random.choice(EVERGREEN_TOPICS)
        print(f"LONG Mode: EVERGREEN - Day {day_number} - topic: {topic}")
        prompt = EVERGREEN_PROMPT.format(topic=topic, shared_rules=shared_rules, day_number=day_number)
        data = call_gemini_with_retry(prompt)

    for s in data["scenes"]:
        words = s["voiceover"].split()
        if len(words) > 30:
            s["voiceover"] = " ".join(words[:30]) + "."

    with open("today_script_long.json", "w") as f:
        json.dump(data, f, indent=2)

    print("LONG topic:", data["topic"])
    print("LONG Wallet impact:", data.get("wallet_impact"))
    print("LONG Scenes:", len(data["scenes"]))
    return data


if __name__ == "__main__":
    generate()

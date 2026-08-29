"""
generate_script_long.py
Trend-research + long-form script generation, independent from the short
pipeline, scheduled at its own optimal time.
"""

import os
import json
import time
import requests
import google.generativeai as genai

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)


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


PROMPT = """You are a Senior Finance Trend Research Analyst AND long-form
YouTube script writer for a US finance channel called MoneyPulse.

STEP 1 - TREND RESEARCH: Look at today's real US finance/business headlines
below. Mentally score candidate stories on Viral Score, Entertainment Score,
Finance Value, US Relevancy, Audience Curiosity. Pick the single best "Topic
of Today".

STEP 2 - SCRIPT: Write a 5-7 minute long-form video script on that topic.
Go deep: background/context, the news itself, why it's happening, historical
comparison, who is affected and how, multiple real examples, plain-English
analysis, what happens next, actionable advice, strong takeaway.
Tone: casual, friendly, smart, not robotic. Use only verified real numbers
from the headlines below - never invent stats.

Return ONLY valid JSON, no markdown:
{
  "topic": "one sentence",
  "why_it_works": "1-2 sentences",
  "title": "compelling title under 100 chars",
  "description": "3-4 sentence description",
  "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "scenes": [
    {"voiceover": "MAX 30 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}
  ]
}
Rules: exactly 14-18 scenes, each voiceover 30 words or FEWER, last scene ends
with a comment-trigger question + follow CTA.

Today's real US finance headlines:
"""


def call_gemini_with_retry(prompt, attempts=3):
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
            time.sleep(10)
    raise last_err


def generate():
    headlines = fetch_headlines()
    data = call_gemini_with_retry(PROMPT + headlines)

    for s in data["scenes"]:
        words = s["voiceover"].split()
        if len(words) > 30:
            s["voiceover"] = " ".join(words[:30]) + "."

    with open("today_script_long.json", "w") as f:
        json.dump(data, f, indent=2)

    print("LONG topic:", data["topic"])
    print("Scenes:", len(data["scenes"]))
    return data


if __name__ == "__main__":
    generate()

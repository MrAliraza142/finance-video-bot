"""
generate_script.py
Fetches recent US finance/business headlines, then uses Gemini to generate
BOTH a short (Shorts, <=60s) and a long (5-7 min) script about the SAME
story, so both formats stay consistent with each other and with the
channel's single content pillar: US personal/business finance news
explained simply for everyday people.
"""

import os
import json
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
    headlines = [
        f"- {a['title']}: {a.get('description') or ''}"
        for a in articles
        if a.get("title")
    ]
    return "\n".join(headlines[:15])


SYSTEM_PROMPT = """You are a Senior Finance Researcher and Script Writer for a
faceless finance YouTube channel called MoneyPulse. The channel's single
content pillar, ALWAYS, is: "US personal and business finance news explained
simply, and how it affects an ordinary person's wallet." No AI avatar/character
is used - videos are text/graphics/chart-based only, narrated by a voiceover.

Given today's real US finance/business headlines, pick the SINGLE best story,
then write TWO versions of that same story:

1. A SHORT version for YouTube Shorts (45-60 seconds spoken total)
2. A LONG version for a regular YouTube video (5-7 minutes spoken total)

Both versions cover the EXACT SAME topic - the long version just goes deeper
(more context, more examples, more background) instead of covering something
different.

Return ONLY valid JSON, no markdown, in this exact shape:

{
  "topic": "the single story both versions are about",
  "why_it_works": "1-2 sentences",
  "short": {
    "title": "punchy title under 60 characters",
    "description": "1-2 sentence description",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "scenes": [
      {"voiceover": "MAX 18 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}
    ]
  },
  "long": {
    "title": "compelling title under 100 characters",
    "description": "3-4 sentence description",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "scenes": [
      {"voiceover": "MAX 30 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}
    ]
  }
}

Rules:
- SHORT: exactly 6-8 scenes, each voiceover line 18 words or FEWER. Structure:
  hook, problem, reality, hidden truth, example, advice, takeaway + comment
  trigger + follow CTA.
- LONG: exactly 18-24 scenes, each voiceover line 30 words or FEWER. Structure:
  hook, background, the news itself, why it's happening, historical context,
  who is affected, multiple examples, plain-English analysis, what happens
  next, advice, takeaway + comment trigger + follow CTA.
- Use only verified, real numbers/facts from the headlines - never invent.
- Casual, friendly, easy English. WORD LIMITS ARE STRICT.
"""


def generate():
    headlines = fetch_headlines()
    model = genai.GenerativeModel("gemini-flash-latest")
    prompt = f"{SYSTEM_PROMPT}\n\nToday's real US finance headlines:\n{headlines}"
    response = model.generate_content(prompt)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text)

    def trim(scenes, max_words):
        for s in scenes:
            words = s["voiceover"].split()
            if len(words) > max_words:
                s["voiceover"] = " ".join(words[:max_words]) + "."

    trim(data["short"]["scenes"], 18)
    trim(data["long"]["scenes"], 30)

    with open("today_script.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Topic:", data["topic"])
    print("Short scenes:", len(data["short"]["scenes"]))
    print("Long scenes:", len(data["long"]["scenes"]))
    return data


if __name__ == "__main__":
    generate()

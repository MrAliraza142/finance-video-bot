"""
generate_script.py
Fetches recent US finance/business headlines (free NewsAPI.org tier),
then uses Google Gemini (free tier) to generate:
  - today's best topic
  - a 45-60 sec TikTok/Shorts script (hook/body/ending)
  - scene-by-scene captions + keywords for stock footage search

Output: writes today_script.json used by later steps.
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


SYSTEM_PROMPT = """You are a Senior Finance Content Strategist and viral short-form
script writer for a faceless finance TikTok/YouTube Shorts channel aimed at a US
audience. No AI avatar/character is used - videos are text/graphics/chart-based only.

Given today's real finance headlines, do the following and return ONLY valid JSON,
no markdown, no explanation:

{
  "topic": "the single best topic for today, one clear sentence",
  "why_it_works": "1-2 sentences on why this will perform well",
  "title": "punchy video title, under 60 characters",
  "description": "1-2 sentence YouTube/TikTok description",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "scenes": [
    {
      "voiceover": "the exact line the narrator says in this scene (one sentence or two, ~6-9 seconds spoken)",
      "on_screen_text": "short punchy caption text to display on screen for this scene (max 8 words)",
      "footage_keyword": "1-3 word search term for free stock footage that fits this scene, e.g. 'stock market chart', 'city skyline', 'person checking phone'"
    }
  ]
}

Rules:
- 6 to 8 scenes total, each ~6-9 seconds of spoken voiceover, total video 45-60 seconds
- Scene 1 must be a strong hook (shocking or emotional, makes people stop scrolling)
- Use only verified, real numbers/facts from the provided headlines - do not invent statistics
- Casual, friendly, easy English. No jargon without a quick plain-English explanation.
- Last scene must include a comment-trigger question and a "follow for tomorrow" call to action
"""


def generate():
    headlines = fetch_headlines()
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"{SYSTEM_PROMPT}\n\nToday's real US finance headlines:\n{headlines}"
    response = model.generate_content(prompt)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text)

    with open("today_script.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Script generated:", data["title"])
    return data


if __name__ == "__main__":
    generate()
